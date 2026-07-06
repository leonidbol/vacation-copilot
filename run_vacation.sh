#!/usr/bin/env bash
set -euo pipefail

# 1️⃣ Safely export variables from your local .env if it exists
if [ -f .env ]; then
  set +e  # temporarily relax error checking for the export pipeline
  export $(grep -v '^#' .env | xargs) 2>/dev/null
  set -e  # turn strict error checking back on
fi

# Fail gracefully if no valid keys are configured
if [[ -z "${GEMINI_API_KEY:-}" && -z "${GOOGLE_CLOUD_PROJECT:-}" ]]; then
  echo "❌ Error: Environment not configured."
  echo "Please copy .env.example to .env and fill in your credentials."
  exit 1
fi

# Restrict credentials file permissions if using a service account JSON path
if [[ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" && -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]]; then
  chmod 600 "$GOOGLE_APPLICATION_CREDENTIALS"
fi

# Activate virtual environment if it exists locally
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# 2️⃣ Execute the Agent directly in interactive foreground mode to stream the output
LOG="server.log"
rm -f "$LOG" # Clean old traces

echo "🚀 Initializing Vacation Copilot..."
echo -e "\n===== LIVE ITINERARY ====="

# Running without the background daemon flags forces the CLI to run synchronously
# and dump the full model response directly to the pipeline.
uv run agents-cli run \
  "I need a full 5‑day itinerary for a family vacation in Tokyo, including kid‑friendly activities, dining suggestions, and a brief packing list." \
  2>&1 | tee "$LOG"

echo -e "==========================\n"

# 3️⃣ Extract the Session ID from the log file
SESSION_ID=$(grep -i "Session:" "$LOG" | head -n1 | awk '{print $NF}' || true)

if [[ -n "$SESSION_ID" ]]; then
  echo "✅ Itinerary successfully generated and logged!"
  echo "🆔 Session ID: $SESSION_ID"
else
  echo "⚠️ Run finished, but no explicit Session ID was captured. Check your API key configuration."
fi

# 4️⃣ Clean up workspace environment
echo "🛑 Cleaning up workspace..."
uv run agents-cli run --stop-server >/dev/null 2>&1 || true
echo "🏁 Process complete"
