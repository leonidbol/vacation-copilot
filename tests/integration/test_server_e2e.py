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

"""End-to-end integration test suite for the FastAPI application server."""
from __future__ import annotations
from aiohttp import web_fileresponse
from aiohttp import web_fileresponse
from aiohttp import web_fileresponse
from aiohttp import web_fileresponse


import json
import logging
import os
import subprocess
import sys
import threading
import time
from collections.abc import Iterator
from typing import Any

import pytest
import requests
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging infrastructure
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000"
STREAM_URL = f"{BASE_URL}/run_sse"
FEEDBACK_URL = f"{BASE_URL}/feedback"

HEADERS = {"Content-Type": "application/json"}


def is_quota_error(exception: Exception) -> bool:
    """Predicate function for tenacity to determine if an error is a quota issue."""
    error_msg = str(exception)
    # Catch both the generic exception string and the official API error strings
    return "429" in error_msg or "Resource Exhausted" in error_msg or "Quota exceeded" in error_msg


def log_output(pipe: Any, log_func: Any) -> None:
    """Read stream lines from a pipe sequentially and route them to a logger."""
    for line in iter(pipe.readline, ""):
        log_func(line.strip())


def start_server() -> subprocess.Popen[str]:
    """Spawn the FastAPI server instance in an isolated background subprocess."""
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.fast_api_app:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]
    env = os.environ.copy()
    env["INTEGRATION_TEST"] = "TRUE"
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )

    # Launch tracking threads to capture runtime server traces in real-time
    threading.Thread(
        target=log_output, args=(process.stdout, logger.info), daemon=True
    ).start()
    threading.Thread(
        target=log_output, args=(process.stderr, logger.error), daemon=True
    ).start()

    return process


def wait_for_server(timeout: int = 90, interval: int = 1) -> bool:
    """Block execution until the background server boundary responds to health checks."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=10)
            if response.status_code == 200:
                logger.info("Server boundary verified alive and responsive.")
                return True
        except RequestException:
            pass
        time.sleep(interval)
    logger.error(f"Server target failed to bind within the allocated {timeout}s window.")
    return False


@pytest.fixture(scope="session")
def server_fixture(request: Any) -> Iterator[subprocess.Popen[str]]:
    """Session-scoped fixture providing an active, isolated execution server boundary."""
    logger.info("Initializing background server process layout...")
    server_process = start_server()
    if not wait_for_server():
        pytest.fail("Aborting integration run: HTTP server boundary failed to initialize.")
    logger.info("Server boundary fully attached.")

    def stop_server() -> None:
        logger.info("Tearing down background server process layout...")
        server_process.terminate()
        server_process.wait()
        logger.info("Background server clean exit confirmed.")

    request.addfinalizer(stop_server)
    yield server_process


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=10, max=60),
    retry=retry(is_quota_error),
    reraise=True
)
def test_chat_stream(server_fixture: subprocess.Popen[str]) -> None:
    """Verify that the HTTP streaming boundary processes real-time SSE event tokens."""
    logger.info("Executing E2E Chat Stream tracking sequence...")
    user_id = "test_user_123"
    session_data = {"state": {"preferred_language": "English", "visit_count": 1}}

    # 1. Establish an active session target configuration
    session_url = f"{BASE_URL}/apps/app/users/{user_id}/sessions"
    session_response = requests.post(
        session_url,
        headers=HEADERS,
        json=session_data,
        timeout=60,
    )
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # 2. Inject a payload stream sequence targeting the unified application agent
    data = {
        "app_name": "app",
        "user_id": user_id,
        "session_id": session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": "Hi! I am ready to schedule a trip."}],
        },
        "streaming": True,
    }
    response = requests.post(
        STREAM_URL, headers=HEADERS, json=data, stream=True, timeout=60
    )
    
    # Fix: Raise a string message that guarantees the retry predicate triggers
    if response.status_code == 429:
        raise RuntimeError("Quota exceeded: 429 Resource Exhausted")

    # Ensure we got a successful stream start before proceeding to read chunks    
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    # 3. Parse and accumulate incoming Server-Sent Events (SSE) data segments
    events = []
    for line in response.iter_lines():
        if line:
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                event_json = line_str[6:]
                event = json.loads(event_json)
                events.append(event)

    assert events, "The SSE channel failed to stream valid token blocks back to the client."
    
    has_text_content = False
    for event in events:
        content = event.get("content")
        if (
            content is not None
            and content.get("parts")
            and any(part.get("text") for part in content["parts"])
        ):
            has_text_content = True
            break

    assert has_text_content, "The event stream failed to emit valid textual context segments."


def test_chat_stream_error_handling(server_fixture: subprocess.Popen[str]) -> None:
    """Verify that malformed or non-compliant payloads throw clear validation exceptions."""
    logger.info("Executing E2E Input Error Handling verification...")
    data = {
        "input": {"messages": [{"type": "invalid_type", "content": "Cause an error"}]}
    }
    response = requests.post(
        STREAM_URL, headers=HEADERS, json=data, stream=True, timeout=10
    )

    assert response.status_code == 422, (
        f"Expected validation status code 422, received alternate code: {response.status_code}"
    )


def test_collect_feedback(server_fixture: subprocess.Popen[str]) -> None:
    """Verify that structured feedback metrics pass through the ingest endpoint cleanly."""
    logger.info("Executing E2E Telemetry Feedback tracking verification...")
    feedback_data = {
        "score": 5,
        "user_id": "test-user-456",
        "session_id": "test-session-456",
        "text": "Unified flat agent execution trajectory is performing flawlessly.",
    }

    response = requests.post(
        FEEDBACK_URL, json=feedback_data, headers=HEADERS, timeout=10
    )
    assert response.status_code == 200