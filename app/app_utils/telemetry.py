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

import logging
import os

logger = logging.getLogger(__name__)


def setup_telemetry() -> str | None:
    """Configure OpenTelemetry and GenAI telemetry with GCS upload hooks.
    
    Expects LOGS_BUCKET_NAME to be the raw bucket name string (e.g. 'my-bucket').
    """
    bucket = os.environ.get("LOGS_BUCKET_NAME")
    capture_content = os.environ.get(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false"
    )
    
    # Strip any accidentally passed 'gs://' prefixes to safeguard URI parsing
    if bucket:
        bucket = bucket.replace("gs://", "").strip("/")

    if bucket and capture_content != "false":
        logger.info(
            "Prompt-response telemetry active - Privacy Mode: NO_CONTENT "
            "(Metadata only; raw message strings are completely omitted)."
        )
        
        # Enforce strict compliance data guardrails
        os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "NO_CONTENT"
        
        # Configure runtime OpenTelemetry variables
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT", "jsonl")
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK", "upload")
        os.environ.setdefault(
            "OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental"
        )
        
        commit_sha = os.environ.get("COMMIT_SHA", "dev")
        os.environ.setdefault(
            "OTEL_RESOURCE_ATTRIBUTES",
            f"service.namespace=vacation-copilot,service.version={commit_sha}",
        )
        
        path = os.environ.get("GENAI_TELEMETRY_PATH", "completions")
        os.environ.setdefault(
            "OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH",
            f"gs://{bucket}/{path}",
        )
    else:
        logger.info(
            "Prompt-response logging disabled. To activate, set LOGS_BUCKET_NAME to your raw "
            "GCS bucket identifier (e.g., 'your-telemetry-bucket') and set "
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT='true'."
        )

    return bucket