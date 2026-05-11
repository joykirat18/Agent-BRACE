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

import os
import json
import re
import textworld
from typing import List

from meow_tea_train.agentic_menu.base.env import BaseEnv
from meow_tea_train.agentic_menu.sync_textworld.env import TextWorldEnv, AlfWorldEnv


class EnvTrajectoryCollector:
    def __init__(self, env_name: str, instance_dir: str, instance_id: str, task_prefix: str):
        self.env_name = env_name
        self.instance_dir = instance_dir
        self.instance_id = instance_id
        self.task_prefix = task_prefix
        self.env = self._get_env()
        self.game_logistics = self._load_env_logistics()

    def _get_env(self) -> BaseEnv:
        if self.env_name == "textworld":
            return TextWorldEnv(instance_file=os.path.join(self.instance_dir, f"{self.task_prefix}_{self.instance_id}.z8"))
        elif self.env_name == "alfworld":
            return AlfWorldEnv(instance_file=os.path.join(self.instance_dir, f"{self.task_prefix}_{self.instance_id}.tw-pddl"))
        else:
            raise ValueError(f"Unknown environment name: {self.env_name}")

    def _load_env_logistics(self):
        logistics = {
            "objective": None,
            "walkthrough": None
        }

        if isinstance(self.env, TextWorldEnv):
            json_instance_file = os.path.join(self.instance_dir, f"{self.task_prefix}_{self.instance_id}.json")
            if not os.path.exists(json_instance_file):
                # Textworld has to use *.json file to load the game logistics
                raise FileNotFoundError(f"JSON file for instance {self.instance_id} not found in {self.instance_dir}")
            
            game = textworld.generator.Game.load(json_instance_file)
            logistics["objective"] = game.objective
            logistics["walkthrough"] = game.walkthrough

        elif isinstance(self.env, AlfWorldEnv):
            pddl_instance_file = os.path.join(self.instance_dir, f"{self.task_prefix}_{self.instance_id}.tw-pddl")
            with open(pddl_instance_file, 'r') as f:
                game_dict = json.loads(f.read())
                logistics["walkthrough"] = game_dict["walkthrough"]
                # AlfWorld does not have a clear "objective" field in the JSON file
                # We extract it from the initial state of the game
                objective = ""
                match = re.search(r"Your task is to:\s*(.*)", self.env.init_state)
                if match:
                    objective = match.group(1).strip()

                logistics["objective"] = objective
        else:
            raise ValueError("Unsupported environment type for loading logistics.")

        return logistics

    def get_trajectory_given_actions(self, action_seq: List[str]) -> List[str]:
        trajectory = []
        trajectory.append(self.env.init_state)
        for action in action_seq:
            next_state, _, _ = self.env.one_step(action)
            trajectory.append(action)
            trajectory.append(next_state)
        
        return trajectory