# Copyright 2025 Anonymous Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
#
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re

import textworld
from textworld.agents import HumanAgent
from textworld.core import GameState
from textworld.envs.wrappers import Filter
from alfworld.agents.environment.alfred_tw_env import AlfredDemangler
from typing import List, Optional, Tuple

from ..base.env import BaseEnv


class TextWorldEnvBase(BaseEnv):
    def __init__(self, instance_file: str):
        self.instance_file = instance_file
        self.game_agent = HumanAgent()


    def init_env(self):
        pass


    def _sanitize_command(self, command: str):
        """Fix error of Z-machine: DUMB-FROTZ: unknown escape char: """
        if not isinstance(command, str):
            return ""
        
        # Remove all backslashes - they're rarely valid in text adventure commands
        return command.replace('\\', '').strip()


    def _safe_step(self, command: str):
        """Safely execute a step, falling back to empty command on Unicode errors"""
        command = self._sanitize_command(command)
        try:
            return self.env.step(command)
        except:
            print(f"Game backend error with command '{command}'")
            return self.env.step("")
        
    
    def one_step(self, command: str):
        pass


    def replay(self, commands: List[str]):
        pass

    
    def get_total_rewards(self):
        # For Textworld games, the total reward is typically the max score of the game.
        return 1.0

    def get_raw_state_facts_str(self) -> str:
        """Return a human-readable string of ground-truth world facts for reward evaluation.

        Subclasses that track the last game state should override this.
        Returns an empty string when unavailable.
        """
        return ""

    @staticmethod
    def _tw_entity_label(game, var_id: str) -> str:
        """Map a logic variable id (e.g. r_1, c_0) to the in-game entity name when available."""
        if var_id == "P":
            return "player"
        if game is not None:
            info = game.infos.get(var_id)
            if info is not None and getattr(info, "name", None):
                return info.name
        return var_id

    @staticmethod
    def _tw_format_proposition(game, prop) -> str:
        args = [TextWorldEnvBase._tw_entity_label(game, a.name) for a in prop.arguments]
        return f"{prop.name}({', '.join(args)})"


class TextWorldEnv(TextWorldEnvBase):
    def __init__(self, instance_file: str):
        super().__init__(instance_file)
        self.init_env()


    def init_env(self):
        # Load textworld game:
        textworld_infos = textworld.EnvInfos(
            feedback=True,    # Response from the game after typing a text command.
            description=True, # Text describing the room the player is currently in.
            inventory=True    # Text describing the player's inventory.
        )
        self.env = textworld.start(self.instance_file, request_infos=textworld_infos, wrappers=self.game_agent.wrappers)
        self.game_agent.reset(self.env)
        # Get the initial observation text
        self.init_state = self.format_observation(self.env.reset())


    def format_observation(self, game_state: GameState):
        """
        Get the observation at each step, consisting of `room description`, `game feedback`, `inventory`, and `last action`, according to KG-A2C paper.
        Descriptions:
            - room description: agent's current location
            - game feedback: outputs of game simulator given agent's previous action
            - inventory: agent's inventory list
        """
        room_id = None
        for s in game_state._facts:
            if s.name == "at" and s.arguments[0].name == "P":
                room_id = s.arguments[1].name
                break
        if not room_id or room_id not in game_state.game.infos:
            raise ValueError
        room_desc = f"You are now in the {game_state.game.infos[room_id].name}.\n"

        feedback = self._extract_essential_feedback(game_state.feedback) + '\n'

        inventory = game_state.inventory

        admissible_commands = game_state.admissible_commands

        admissible_commands_str = "\nAdmissible commands: " + ", ".join(admissible_commands)

        obs = room_desc + feedback + inventory + admissible_commands_str

        return obs


    def one_step(self, command: str):
        game_state, reward, done = self._safe_step(command)
        self._last_game_state = game_state
        obs = self.format_observation(game_state)
        return obs, done, reward

    @staticmethod
    def _tw_entity_label(game, var_id: str) -> str:
        """Map a logic variable id (e.g. r_1, c_0) to the in-game entity name when available."""
        if var_id == "P":
            return "player"
        if game is not None:
            info = game.infos.get(var_id)
            if info is not None and getattr(info, "name", None):
                return info.name
        return var_id

    @staticmethod
    def _tw_format_proposition(game, prop) -> str:
        args = [TextWorldEnv._tw_entity_label(game, a.name) for a in prop.arguments]
        return f"{prop.name}({', '.join(args)})"

    def get_raw_state_facts_str(self) -> str:
        """Summarize ground-truth state from the last step for belief-state evaluation.

        Combines narrative fields (objective, description, inventory), actionable
        commands, entity lists, and logic facts with entity ids resolved via
        ``game.infos`` where possible.
        """
        gs = getattr(self, "_last_game_state", None)
        if gs is None:
            return ""

        def _truncate(text: str, max_len: int = 4000) -> str:
            text = text.strip()
            if len(text) <= max_len:
                return text
            return text[: max_len - 24].rstrip() + "\n...[truncated]..."

        game = gs.get("game")
        lines: List[str] = ["=== Ground-truth environment state (belief checking) ==="]

        obj = gs.get("objective")
        if isinstance(obj, str) and obj.strip():
            lines.append("Objective:")
            lines.append(_truncate(obj, 3500))

        lc = gs.get("last_command")
        if isinstance(lc, str) and lc.strip():
            lines.append(f"Last command: {lc.strip()}")

        progress_bits: List[str] = []
        for key, label in (
            ("score", "score"),
            ("moves", "moves"),
            ("won", "won"),
            ("lost", "lost"),
            ("done", "done"),
        ):
            val = gs.get(key)
            if val is not None:
                progress_bits.append(f"{label}={val}")
        if progress_bits:
            lines.append("Progress: " + ", ".join(progress_bits))

        player_room: Optional[str] = None
        try:
            for f in gs._facts:
                if f.name == "at" and len(f.arguments) >= 2 and f.arguments[0].name == "P":
                    player_room = self._tw_entity_label(game, f.arguments[1].name)
                    break
        except Exception:
            player_room = None
        if player_room:
            lines.append(f"Player location (room): {player_room}")

        try:
            inv = gs.get("inventory")
            if isinstance(inv, str) and inv.strip():
                lines.append("Inventory:")
                lines.append(_truncate(inv, 2000))
        except Exception:
            pass

        adm = gs.get("admissible_commands")
        if isinstance(adm, list) and adm:
            lines.append("Admissible commands: " + ", ".join(str(c) for c in adm))

        ent = gs.get("entities")
        if isinstance(ent, list) and ent:
            lines.append("Named entities: " + ", ".join(str(e) for e in ent))

        te = gs.get("typed_entities")
        if isinstance(te, list) and te:
            typed_parts: List[str] = []
            for item in te:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    typed_parts.append(f"{item[0]} ({item[1]})")
                else:
                    typed_parts.append(str(item))
            if typed_parts:
                lines.append("Typed entities: " + "; ".join(typed_parts))

        try:
            desc = gs.get("description")
            if isinstance(desc, str) and desc.strip():
                lines.append("Room description:")
                lines.append(_truncate(desc))
        except Exception:
            pass

        pred_priority = {
            "at": 0,
            "on": 1,
            "in": 2,
            "open": 3,
            "closed": 4,
            "locked": 5,
            "match": 6,
        }
        connectivity = frozenset(
            {"free", "north_of", "south_of", "east_of", "west_of", "link"}
        )

        def _fact_sort_key(prop):
            name = prop.name
            p = pred_priority.get(name, 50)
            if name in connectivity:
                p = 200
            arg_key = tuple(a.name for a in prop.arguments)
            return (p, name, arg_key)

        try:
            facts = sorted(gs._facts, key=_fact_sort_key)
            fact_strs = [self._tw_format_proposition(game, f) for f in facts]
            lines.append("Logical facts (entity names resolved where available):")
            if fact_strs:
                lines.append("  " + "; ".join(fact_strs))
            else:
                lines.append("  (none)")
        except Exception:
            lines.append("Logical facts: (unavailable)")

        return "\n".join(lines)

    def replay(self, commands: List[str]) -> Tuple[str, bool, float]:
        """
        Reset the game environment, restart game, and replay the sequence of actions.
        Return observation (str), if has won the game (bool), and the reward at the step (float) 
        """
        is_winning = False
        for command in commands:
            game_state, reward, done = self._safe_step(command)
            obs = self.format_observation(game_state)
            if done:
                is_winning = True
                break  # Game completed early
        return obs, is_winning, reward


    def _extract_essential_feedback(self, text):
        """
        Extract essential feedback from TextWorld output.
        This extracts room descriptions and action feedback without duplication.
        """
        result = []
        
        # Extract room descriptions - between room header and prompt
        room_pattern = r'-= (.+?) =-\n([\s\S]*?)(?=\s*>|$)'
        room_matches = re.finditer(room_pattern, text)
        
        for match in room_matches:
            room_desc = match.group(2).strip()
            if room_desc:
                # Split by lines and add non-empty ones
                lines = [line.strip() for line in room_desc.split('\n') if line.strip()]
                result.extend(lines)
        
        # Extract action feedback - lines before a prompt that aren't part of headers
        action_pattern = r'^([^-=>\n][^\n]*?)(?=\n\s*>)'
        action_matches = re.finditer(action_pattern, text, re.MULTILINE)
        
        for match in action_matches:
            action = match.group(1).strip()
            if action and action not in result:
                result.append(action)
        
        # Remove duplicates while preserving order
        return '\n'.join(dict.fromkeys(result))


class AlfWorldEnv(TextWorldEnvBase):
    def __init__(self, instance_file: str):
        super().__init__(instance_file)
        self.init_env()
        

    def init_env(self):
        # Load alfworld game
        self.infos = textworld.EnvInfos(
            score=True,
            max_score=True,
            won=True,
            lost=True,
            feedback=True,
            inventory=True,
            admissible_commands=True,
            moves=True,
            facts=True,        # full logical world facts for get_raw_state_facts_str
            game=True,         # game object for entity-id → name resolution
            entities=True,     # named entity list
            description=True,  # room description text
            extras=["walkthrough", "expert_plan"],
        )
        self.env = textworld.start(
            self.instance_file, self.infos, wrappers=[Filter, AlfredDemangler()]
        )
        self.game_agent.reset(self.env)
        # Get the initial observation text
        init_obs, init_extras = self.env.reset()
        self.init_state = self.format_observation(init_obs, init_extras)


    def format_observation(self, obs: str, extras: dict) -> str:
        """Format observation to match TextWorld format: feedback + inventory + admissible commands."""
        feedback = (extras.get("feedback") or obs or "").strip()
        inventory = (extras.get("inventory") or "").strip()
        admissible_commands = extras.get("admissible_commands") or []

        parts = [feedback]
        if inventory:
            parts.append(inventory)
        if admissible_commands:
            parts.append("\nAdmissible commands: " + ", ".join(admissible_commands))

        return "\n".join(parts)


    def one_step(self, command: str):
        obs, reward, done, extras = self._safe_step(command)
        self._last_extras = extras if isinstance(extras, dict) else {}
        # `done=True` fires on both game-win AND max-steps-reached (timeout).
        # We return `done` to stop the episode in either case, but normalise the
        # reward so the caller can distinguish the two outcomes:
        #   win     → done=True,  reward=1.0
        #   timeout → done=True,  reward=0.0
        # This way agent.py's `if has_won: final_reward_batch[idx] = 1.0` correctly
        # gives 0 reward for timed-out episodes (has_won=True but reward=0 signals
        # timeout; see agent.py for how final_reward is assigned).
        if done:
            won = extras.get('won', False) if isinstance(extras, dict) else False
            reward = 1.0 if won else 0.0
        return self.format_observation(obs, extras), done, reward


    def replay(self, commands: List[str]) -> Tuple[str, bool, float]:
        """
        Reset the game environment, restart game, and replay the sequence of actions.
        This ensures we backtrack correctly to the desired state.
        """
        is_winning = False
        obs, reward, extras = "", 0.0, {}
        for command in commands:
            obs, reward, done, extras = self._safe_step(command)
            self._last_extras = extras if isinstance(extras, dict) else {}
            is_winning = extras.get('won', False) if isinstance(extras, dict) else False
            if done:
                break  # Game completed (won or timed out)
        return self.format_observation(obs, extras), is_winning, reward

    # Schema / static-type predicates in ALFWorld that describe the domain
    # (what types can contain what, which class an entity belongs to, grid
    # coordinates, static capabilities) rather than the dynamic world state.
    # Dropping these keeps the facts list focused on things that actually
    # change — placement, agent location, open/closed, cleaned/heated/cooled —
    # and keeps the belief-reward prompt under the 8k token window.
    _ALFWORLD_SCHEMA_PREDICATES = frozenset({
        "cancontain",
        "objecttype",
        "receptacletype",
        "objectatlocation",
        "receptacleatlocation",
        "isreceptacleobject",
        "sliceable",
        "openable",
        "not_atlocation",
    })

    def get_raw_state_facts_str(self) -> str:
        """Summarise ground-truth state from the last step for belief-state evaluation.

        Mirrors TextWorldEnv.get_raw_state_facts_str but reads from the extras dict
        returned by AlfWorld's Filter-wrapped environment at each step.  Requests
        facts=True, game=True, entities=True, description=True in init_env so that
        logical world facts are available alongside the narrative fields.
        """
        extras = getattr(self, "_last_extras", None)
        if not extras:
            return ""

        def _truncate(text: str, max_len: int) -> str:
            text = text.strip()
            if len(text) <= max_len:
                return text
            return text[: max_len - 24].rstrip() + "\n...[truncated]..."

        game = extras.get("game")
        lines: List[str] = ["=== Ground-truth environment state (belief checking) ==="]

        # Current game feedback (what the agent observes at the current location)
        feedback = extras.get("feedback") or ""
        if feedback.strip():
            lines.append("Current observation:")
            lines.append(_truncate(feedback.strip(), 1500))

        # Progress counters
        progress_bits: List[str] = []
        for key, label in (
            ("score", "score"),
            ("moves", "moves"),
            ("won", "won"),
            ("lost", "lost"),
        ):
            val = extras.get(key)
            if val is not None:
                progress_bits.append(f"{label}={val}")
        if progress_bits:
            lines.append("Progress: " + ", ".join(progress_bits))

        # Inventory
        try:
            inv = extras.get("inventory") or ""
            if inv.strip():
                lines.append("Inventory:")
                lines.append(_truncate(inv, 800))
        except Exception:
            pass

        # Room description
        try:
            desc = extras.get("description") or ""
            if desc.strip():
                lines.append("Room description:")
                lines.append(_truncate(desc, 1500))
        except Exception:
            pass

        # Logical facts — drop schema/type predicates so only dynamic world
        # state (placement, agent location, open/closed, cleaned, heated,
        # cooled, etc.) remains. The full fact list otherwise blows past the
        # 8k-token limit on the belief-reward LLM call.
        pred_priority = {
            "atlocation": 0,
            "holds": 1,
            "inreceptacle": 2,
            "opened": 3,
            "closed": 4,
            "locked": 5,
            "isclean": 6,
            "ishot": 7,
            "iscool": 8,
            "issliced": 9,
        }

        def _fact_sort_key(prop):
            name = prop.name
            p = pred_priority.get(name, 50)
            return (p, name, tuple(a.name for a in prop.arguments))

        try:
            facts = extras.get("facts") or []
            dynamic_facts = [
                f for f in facts
                if f.name not in self._ALFWORLD_SCHEMA_PREDICATES
            ]
            if dynamic_facts:
                sorted_facts = sorted(dynamic_facts, key=_fact_sort_key)
                fact_strs = [self._tw_format_proposition(game, f) for f in sorted_facts]
                joined = "; ".join(fact_strs)
                lines.append("Logical facts (entity names resolved where available):")
                lines.append("  " + _truncate(joined, 2000))
            else:
                lines.append("Logical facts: (unavailable)")
        except Exception:
            lines.append("Logical facts: (unavailable)")

        return "\n".join(lines)