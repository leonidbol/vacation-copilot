# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Literal
from pydantic import BaseModel, Field


class Feedback(BaseModel):
    """Represents validated client feedback for a travel conversation session."""

    # Restrict score to standard 1-5 star scale or 0.0-1.0 binary sentiment
    score: float = Field(
        ..., 
        ge=0, 
        le=5, 
        description="The feedback rating score, bounded between 0 and 5."
    )
    text: str = Field(
        default="", 
        description="Optional additional commentary provided by the traveler."
    )
    log_type: Literal["feedback"] = "feedback"
    service_name: Literal["vacation-copilot"] = "vacation-copilot"
    
    # Require tracking IDs explicitly to guarantee telemetric linkage to chat logs
    user_id: str = Field(
        ..., 
        description="The unique identifier of the traveler giving feedback."
    )
    session_id: str = Field(
        ..., 
        description="The specific conversation session identifier being evaluated."
    )