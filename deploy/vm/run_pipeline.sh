#!/usr/bin/env bash
#runs the thi pipeline like previous "update_data.yml" file
#from a real entry now instead of github actions

# crontab entry on the vm:
# 41 6,9,12 * * * /home/azureuser/thi/deploy/vm/run_pipeline.sh

set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_DIR"

source .venv/bin/activate
set -a
source .env
set +a

LOG_DIR="$REPO_DIR/deploy/vm/logs"
mkdir -p "$LOG_DIR"

RUN_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
STAMP="$(date -u +%Y%m%d_%H%M%S)"
echo "${RUN_TS},scheduled_run" >> "$LOG_DIR/run_timestamps.csv"

python generate_data.py >> "$LOG_DIR/generate_${STAMP}.log" 2>&1
GEN_STATUS=$?
if [ $GEN_STATUS -ne 0 ]; then
    echo "generate_data.py failed (exit ${GEN_STATUS}) — aborting push+notify" >&2
    exit $GEN_STATUS
fi

git config user.email "vm-cron@thi-pipeline.local"
git config user.name "THI VM Cron"
git add docs/data/*.json
git diff --quiet && git diff --staged --quiet || (
    git commit -m "Update weather data [skip ci]" &&
    git push origin HEAD:main
)

# matches current GitHub Actions behavior exactly.
python send_notification.py >> "$LOG_DIR/notify_${STAMP}.log" 2>&1 || true
