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

"""Global pytest configurations and shared test fixtures."""



from __future__ import annotations

import os

# Mute all OpenTelemetry exporters before any Google SDK modules load
os.environ["OTEL_TRACES_EXPORTER"] = "none"
os.environ["OTEL_LOGS_EXPORTER"] = "none"
os.environ["OTEL_METRICS_EXPORTER"] = "none"

import time
from typing import Generator

import pytest
from unittest.mock import AsyncMock

@pytest.fixture(autouse=True)
def pace_free_tier_quota() -> Generator[None, None, None]:
    """Automatically injects a execution delay to respect the 5 RPM free tier API limit.

    To bypass this penalty during offline unit testing or when running against 
    a paid tier endpoint, set the environment variable:
        export DISABLE_QUOTA_PACING=TRUE
    """
    yield
    
    # Check if pacing has been explicitly bypassed for local/mock execution
    if os.environ.get("DISABLE_QUOTA_PACING", "FALSE").upper() == "TRUE":
        return

    # 60 seconds / 5 requests = 12 seconds minimum spacing between live operations
    time.sleep(12)





