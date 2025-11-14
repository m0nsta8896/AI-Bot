#!/bin/bash

# --- Configuration ---
BOT_SCRIPT="Bot.py"
REQUIREMENTS_FILE="requirements.txt"
PYTHON_CMD="python"
RESTART_DELAY=2

# --- Crash Loop Detection Config ---
MAX_FAILURES=3
FAILURE_WINDOW=60
failure_timestamps=()

# --- Path Configuration ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BOT_PATH="$SCRIPT_DIR/$BOT_SCRIPT"
REQUIREMENTS_PATH="$SCRIPT_DIR/$REQUIREMENTS_FILE"

# --- Helper Function ---
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [Wrapper:$BOT_SCRIPT] $1" >&2
}

# --- Pre-Run Checks ---
if ! command -v "$PYTHON_CMD" &> /dev/null; then
    echo "Error: Python command not found: '$PYTHON_CMD'" >&2
    echo "Please check the PYTHON_CMD variable in this script." >&2
    exit 1
fi
if [ ! -f "$BOT_PATH" ]; then
    echo "Error: Bot script not found at: $BOT_PATH" >&2
    exit 1
fi

# --- Requirement Installation ---
if [ -f "$REQUIREMENTS_PATH" ]; then
    log "Installing dependencies..."
    "$PYTHON_CMD" -m pip install -r "$REQUIREMENTS_PATH"
    INSTALL_EXIT_CODE=$?
    if [ $INSTALL_EXIT_CODE -ne 0 ]; then
        log "Error: Failed to install requirements (Exit Code $INSTALL_EXIT_CODE)." >&2
        log "Please check the contents of $REQUIREMENTS_FILE and ensure '$PIP_CMD' is working." >&2
        exit 1
    fi
    log "Dependencies installed successfully."
else
    log "No $REQUIREMENTS_FILE found. Skipping dependency installation."
fi

# --- Secure Key Input ---
read -s -p "Enter Key: " temp_key
echo

# --- Main Execution ---
log "Wrapper script started."
log "Settings: RestartDelay=${RESTART_DELAY}s, CrashLoop=${MAX_FAILURES} failures in ${FAILURE_WINDOW}s"

while true; do
    log "Starting bot..."
    BOT_KEY="$temp_key" "$PYTHON_CMD" "$BOT_PATH"
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        log "Bot shut down gracefully (Exit Code 0). Exiting loop."
        break
    elif [ $EXIT_CODE -eq 130 ] || [ $EXIT_CODE -eq 143 ]; then
        log "Bot stopped by user signal (Code $EXIT_CODE). Exiting loop."
        break
    else
        log "Bot crashed or exited unexpectedly (Exit Code $EXIT_CODE)."
        now=$(date +%s)
        cutoff=$(($now - $FAILURE_WINDOW))
        temp_timestamps=()
        for ts in "${failure_timestamps[@]}"; do
            if [ $ts -gt $cutoff ]; then
                temp_timestamps+=($ts)
            fi
        done
        temp_timestamps+=($now)
        failure_timestamps=("${temp_timestamps[@]}")
        failure_count=${#failure_timestamps[@]}
        if [ $failure_count -ge $MAX_FAILURES ]; then
            log "FATAL: Bot has crashed $failure_count times in the last $FAILURE_WINDOW seconds."
            log "Aborting to prevent rapid crash loop."
            break
        fi
        log "Restarting in $RESTART_DELAY seconds... (Failure $failure_count of $MAX_FAILURES)"
        sleep "$RESTART_DELAY"
    fi
done
unset temp_key
log "Wrapper script finished."