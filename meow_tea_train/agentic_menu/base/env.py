# Copyright 2025 Anonymous Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
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

from abc import ABC, abstractmethod
from typing import Any, Tuple, List


class BaseEnv(ABC):
    """Base abstract class for all environments in the agentic menu."""
    
    def __init__(self, **kwargs):
        """Initialize the environment with configuration parameters."""
        self.config = kwargs
    
    @abstractmethod
    def init_env(self) -> None:
        """Initialize the environment."""
        pass
    
    @abstractmethod
    def one_step(self, action: str) -> Tuple[str, bool, float]:
        """
        Execute one step in the environment.
        
        Args:
            action (str): The action to execute
            
        Returns:
            Tuple[str, bool, float]: (observation, done, reward)
        """
        pass
    
    @abstractmethod
    def replay(self, actions: List[str]) -> Tuple[str, bool, float]:
        """
        Replay a sequence of actions.
        
        Args:
            actions (List[str]): List of actions to replay
            
        Returns:
            Tuple[str, bool, float]: (final_observation, done, final_reward)
        """
        pass
    
    @abstractmethod
    def get_total_rewards(self) -> float:
        """
        Get the maximum possible reward for this environment instance.
        
        Returns:
            float: Maximum total reward
        """
        pass