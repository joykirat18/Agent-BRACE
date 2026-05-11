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

MULTITURN_PROMPT_TEMPLATE = """You are an expert TextWorld game solver. Your goal is to generate the best next action that will lead to winning the game.\n\nEnd your output sequence with an action starting with a verb. Example: open box.\n\nHere is how to win the game:\n{task}\n\nHere is your interactions so far:\n{interactions}"""

SEP_TOKEN="<|im_end|>"