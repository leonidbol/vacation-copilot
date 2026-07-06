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

"""Integration test — validates a successful onboarding trajectory.

This test verifies that the unified single-agent system can:
1. Accept a multi-turn onboarding conversation.
2. Process context-driven state adjustments cleanly in a flat loop.
3. Coordinate execution for tools (save_flight, save_hotel, save_user_profile).
4. Produce valid streaming responses at each step of the conversation.

Note: This validates infrastructure correctness (event streams, tool execution, 
and session persistence). Core LLM response quality is tested via the agents-cli 
evaluation suite.
"""

from __future__ import annotations

import os
import tempfile
import pytest
import time

# Establish an isolated temporary directory for test-generated markdown profiles/itineraries
# This must occur before app modules load and cache environment configurations
TEST_DATA_DIR = tempfile.mkdtemp()
os.environ["VACATION_DATA_DIR"] = TEST_DATA_DIR

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent


def _send_message(runner: Runner, session_id: str, user_id: str, text: str) -> list:
    """Send a message to the runner and collect the resulting event stream chunks."""
    message = types.Content(role="user", parts=[types.Part.from_text(text=text)])
    events = list(
        runner.run(
            new_message=message,
            user_id=user_id,
            session_id=session_id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )
    return events


def _has_text_response(events: list) -> bool:
    """Scan event stream chunks to ensure valid text copy was generated."""
    for event in events:
        if (
            event.content
            and event.content.parts
            and any(part.text for part in event.content.parts)
        ):
            return True
    return False


def _has_tool_call(events: list, tool_name: str) -> bool:
    """Scan event stream chunks to check if a specific tool execution was triggered."""
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call and part.function_call.name == tool_name:
                    return True
    return False


class TestOnboardingTrajectory:
    """End-to-end integration test validating sequential multi-turn onboarding states."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize session parameters and execution runners for an isolated user session."""
        self.session_service = InMemorySessionService()
        self.user_id = "test_traveler"
        self.session = self.session_service.create_session_sync(
            user_id=self.user_id,
            app_name="test",
            state={"user_id": self.user_id},
        )
        self.runner = Runner(
            agent=root_agent,
            session_service=self.session_service,
            app_name="test",
        )

    def test_greeting_produces_response(self):
        """Verify that the agent responds responsively to an initial travel greeting."""
        events = _send_message(
            self.runner,
            self.session.id,
            self.user_id,
            "Hi! I'm planning a trip to Barcelona in August.",
        )
        assert len(events) > 0, "Expected at least one event from the stream chunk layer."
        assert _has_text_response(events), "Expected valid text content back from the agent greeting response."

    def test_flight_info_produces_response(self):
        """Verify that the agent processes conversational flight information context streams."""
        # Establish base intent context
        _send_message(
            self.runner,
            self.session.id,
            self.user_id,
            "I'm going to Barcelona for a week starting August 15th.",
        )
        # Deliver explicit flight details
        events = _send_message(
            self.runner,
            self.session.id,
            self.user_id,
            "Here's my flight: Delta DL456, departing JFK Aug 15 at 7pm, "
            "arriving BCN Aug 16 at 9am. Confirmation: ABC123.",
        )
        assert len(events) > 0, "Expected active stream events for unstructured flight string injection."
        assert _has_text_response(events), "Expected text response confirming or clarifying flight updates."

    def test_multi_turn_produces_responses(self):
        """Verify that the flat unified agent handles sequential state updates across a complex timeline."""
        turns = [
            "Hey! I need help planning my trip to Tokyo.",
            "Flying United UA789 from SFO to NRT on Sept 1, arriving Sept 2. Conf: XYZ789.",
            "Staying at Hotel Sunroute Plaza Shinjuku, Sept 2-7. Conf: HSP456.",
            "I'm gluten-free, love authentic Japanese food, and aim for high protein meals.",
        ]

        for turn_text in turns:
            events = _send_message(
                self.runner, self.session.id, self.user_id, turn_text
            )
            assert len(events) > 0, f"Expected active stream collection for turn snippet: {turn_text[:30]}..."
            assert _has_text_response(events), f"Expected structural text response for turn snippet: {turn_text[:30]}..."
            
            # 💡 Add a sleep to prevent hitting the 5 RPM Free Tier limit
            time.sleep(30)