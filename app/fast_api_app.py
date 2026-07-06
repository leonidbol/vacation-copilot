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

"""FastAPI entry point for the Vacation Copilot service application."""

from __future__ import annotations

import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI
import google.auth
from google.adk.cli.fast_api import get_fast_api_app

from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback

# 1. Initialize environments and global telemetry configurations
load_dotenv()
setup_telemetry()


# 2. Setup standard structural fallback logger for local development
class MockGCPLogger:
    """Fallback logger that mimics Cloud Logging behavior for local testing."""
    def __init__(self):
        self.python_logger = logging.getLogger(__name__)

    def log_struct(self, info: dict, severity: str = "INFO"):
        self.python_logger.info(f"[{severity}] Struct: {info}")


logger = MockGCPLogger()

# 3. Gracefully attempt cloud-native resolution if not in a testing environment
try:
    if (
        "INTEGRATION_TEST" not in os.environ
        and "PYTEST_CURRENT_TEST" not in os.environ
    ):
        import google.cloud.logging as google_cloud_logging
        _, project_id = google.auth.default()
        logging_client = google_cloud_logging.Client()
        logger = logging_client.logger(__name__)
except Exception:
    # Fail silently back to standard console logging if running locally or offline
    pass

# 4. Resolve CORS and backend storage pathways
allow_origins = (
    [org.strip() for org in os.getenv("ALLOW_ORIGINS", "").split(",") if org.strip()]
    if os.getenv("ALLOW_ORIGINS")
    else None
)

logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")
artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
session_service_uri = None

# 5. Build the managed application instance
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=artifact_service_uri,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
    otel_to_cloud=True,
)

app.title = "vacation-copilot"
app.description = "API for interacting with the Agent vacation-copilot"


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log runtime system feedback from users.

    Args:
        feedback: The structured feedback schema content to log.

    Returns:
        A dictionary indicating execution state.
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)