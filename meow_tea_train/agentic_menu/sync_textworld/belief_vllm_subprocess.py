# Copyright 2025 Anonymous Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
#
# You may not use this file except in compliance with the License.

"""
Dedicated-process vLLM for belief-state rollouts.

Policy vLLM (TP>1) and belief vLLM (TP=1) cannot share one Python interpreter
because vLLM uses a single global tensor-parallel group. This module runs
``LLM()`` in a child process with ``CUDA_VISIBLE_DEVICES`` set to the belief
GPU index so per-token logprobs use the normal vLLM API (no HTTP).
"""

from __future__ import annotations

import logging
import multiprocessing as mp
import queue
import threading
import traceback
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _sampling_params_to_dict(sp: Any) -> Dict[str, Any]:
    if hasattr(sp, "to_dict"):
        return dict(sp.to_dict())
    keys = (
        "n",
        "temperature",
        "max_tokens",
        "top_p",
        "top_k",
        "logprobs",
        "detokenize",
        "repetition_penalty",
        "stop_token_ids",
        "ignore_eos",
    )
    out: Dict[str, Any] = {}
    for k in keys:
        if hasattr(sp, k):
            v = getattr(sp, k)
            if v is not None:
                out[k] = v
    return out


def _dict_to_sampling_params(d: Dict[str, Any]) -> Any:
    from vllm import SamplingParams

    return SamplingParams(**d)


def _extract_logprob(step_lp: Any, token_id: int) -> float:
    if not step_lp or not isinstance(step_lp, dict):
        return 0.0
    lp = step_lp.get(int(token_id))
    if lp is None:
        return 0.0
    return float(getattr(lp, "logprob", lp))


def _belief_vllm_worker_main(
    cuda_visible_device_index: str,
    cmd_q: mp.Queue,
    res_q: mp.Queue,
) -> None:
    # Must run before importing torch/vLLM (``Process.initializer`` is not portable under Ray).
    import os

    os.environ["CUDA_VISIBLE_DEVICES"] = str(cuda_visible_device_index)

    from vllm import LLM
    from vllm.inputs.data import TokensPrompt

    llm: Any = None

    def _free() -> None:
        nonlocal llm
        if llm is not None:
            del llm
            llm = None
        import gc

        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

    while True:
        try:
            item = cmd_q.get()
        except (EOFError, KeyboardInterrupt):
            break
        if not isinstance(item, tuple) or len(item) != 3:
            continue
        req_id, cmd, payload = item
        try:
            if cmd == "shutdown":
                _free()
                res_q.put((req_id, True, None))
                break
            if cmd == "park":
                _free()
                res_q.put((req_id, True, None))
                continue
            if cmd in ("init", "reload"):
                _free()
                assert isinstance(payload, dict)
                model_path = payload["model_path"]
                kw = dict(payload["llm_kwargs"])
                llm = LLM(model=model_path, **kw)
                res_q.put((req_id, True, None))
                continue
            if cmd == "generate":
                assert llm is not None, "belief vLLM worker: engine not loaded"
                assert isinstance(payload, dict)
                p_ids_batch: List[List[int]] = payload["prompt_token_ids"]
                sp = _dict_to_sampling_params(payload["sampling_params"])
                tokens_in = [TokensPrompt(prompt_token_ids=list(p)) for p in p_ids_batch]
                outputs = llm.generate(tokens_in, sampling_params=sp)
                serial: List[Dict[str, Any]] = []
                for out in outputs:
                    seq = out.outputs[0]
                    r_ids = [int(t) for t in seq.token_ids]
                    old_lps: List[float] = []
                    if seq.logprobs is not None:
                        for j, tid in enumerate(r_ids):
                            step_lp = seq.logprobs[j] if j < len(seq.logprobs) else None
                            old_lps.append(_extract_logprob(step_lp, tid))
                    else:
                        old_lps = [0.0] * len(r_ids)
                    text = seq.text if getattr(seq, "text", None) else ""
                    serial.append(
                        {
                            "token_ids": r_ids,
                            "sampled_token_logprobs": old_lps,
                            "text": text,
                        }
                    )
                res_q.put((req_id, True, serial))
                continue
            res_q.put((req_id, False, f"unknown cmd: {cmd}"))
        except Exception as e:
            tb = traceback.format_exc()
            res_q.put((req_id, False, f"{e}\n{tb}"))


@dataclass
class _SubSeqOut:
    token_ids: List[int]
    sampled_token_logprobs: List[float]
    text: str


@dataclass
class _SubCompletionOutput:
    outputs: List[_SubSeqOut]


class BeliefVLLMSubprocessClient:
    """
    Parent-side handle; ``generate`` is compatible with
    ``BeliefStateLMTrainer._generate_batch_vllm`` (via ``sampled_token_logprobs``).
    """

    _is_subprocess_client = True

    def __init__(
        self,
        process: mp.context.BaseProcess,
        cmd_q: mp.Queue,
        res_q: mp.Queue,
        *,
        timeout_s: float = 7200.0,
    ):
        self._proc = process
        self._cmd_q = cmd_q
        self._res_q = res_q
        self._timeout_s = timeout_s
        self._parked = False
        self._rpc_lock = threading.Lock()
        self._next_req = 0

    def _next_request_id(self) -> int:
        # Only called while _rpc_lock is held, so no separate lock needed.
        self._next_req += 1
        return self._next_req

    def _rpc(self, cmd: str, payload: Any) -> Any:
        import time

        # Serialize RPCs: the subprocess worker is a single-threaded command loop,
        # so overlapping requests from multiple threads would produce interleaved
        # responses that could be silently discarded, causing hangs.
        with self._rpc_lock:
            req_id = self._next_request_id()
            self._cmd_q.put((req_id, cmd, payload))
            deadline = time.monotonic() + self._timeout_s
            while True:
                remaining = max(0.1, deadline - time.monotonic())
                try:
                    rid, ok, data = self._res_q.get(timeout=min(remaining, 60.0))
                except queue.Empty as e:
                    if time.monotonic() >= deadline:
                        raise TimeoutError(f"belief vLLM subprocess RPC {cmd!r} timed out") from e
                    continue
                if rid != req_id:
                    # Stale response from a timed-out prior call — discard and keep waiting.
                    continue
                if not ok:
                    raise RuntimeError(f"belief vLLM subprocess error: {data}")
                return data

    @classmethod
    def start(
        cls,
        *,
        model_path: str,
        cuda_visible_device_index: int,
        llm_kwargs: Dict[str, Any],
        timeout_s: float = 7200.0,
    ) -> BeliefVLLMSubprocessClient:
        ctx = mp.get_context("spawn")
        cmd_q = ctx.Queue()
        res_q = ctx.Queue()
        proc = ctx.Process(
            target=_belief_vllm_worker_main,
            args=(str(int(cuda_visible_device_index)), cmd_q, res_q),
            name="belief-vllm-worker",
            daemon=True,
        )
        proc.start()
        client = cls(proc, cmd_q, res_q, timeout_s=timeout_s)
        client._rpc(
            "init",
            {"model_path": model_path, "llm_kwargs": llm_kwargs},
        )
        client._parked = False
        logger.info(
            "[BeliefVLLMSubprocessClient] Started worker (CUDA_VISIBLE_DEVICES=%s in child)",
            cuda_visible_device_index,
        )
        return client

    def park(self) -> None:
        self._rpc("park", None)
        self._parked = True

    def reload(self, model_path: str, llm_kwargs: Dict[str, Any]) -> None:
        self._rpc("reload", {"model_path": model_path, "llm_kwargs": llm_kwargs})
        self._parked = False

    def ensure_loaded(self, model_path: str, llm_kwargs: Dict[str, Any]) -> None:
        if self._parked:
            self.reload(model_path, llm_kwargs)

    def generate(self, prompts: Any, sampling_params: Any) -> List[Any]:
        p_ids_batch: List[List[int]] = []
        for p in prompts:
            if hasattr(p, "prompt_token_ids"):
                p_ids_batch.append(list(p.prompt_token_ids))
            else:
                p_ids_batch.append(list(p["prompt_token_ids"]))
        payload = {
            "prompt_token_ids": p_ids_batch,
            "sampling_params": _sampling_params_to_dict(sampling_params),
        }
        serial = self._rpc("generate", payload)
        assert isinstance(serial, list)
        out_list: List[_SubCompletionOutput] = []
        for item in serial:
            so = _SubSeqOut(
                token_ids=item["token_ids"],
                sampled_token_logprobs=item["sampled_token_logprobs"],
                text=item.get("text") or "",
            )
            out_list.append(_SubCompletionOutput(outputs=[so]))
        return out_list

    def close(self) -> None:
        if self._proc.is_alive():
            try:
                self._rpc("shutdown", None)
            except Exception:
                pass
            self._proc.join(timeout=30.0)
            if self._proc.is_alive():
                self._proc.kill()
                self._proc.join(timeout=10.0)
