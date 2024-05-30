#!/bin/bash

# Name of the MS Teams PWA window
WINDOW_NAME="Microsoft Teams"

# Interval between interactions (in seconds)
INTERVAL=300  # 5 minutes

# Control file to stop the script
CONTROL_FILE="/tmp/stop_keep_active"

# Log file
LOG_FILE="/tmp/keep_active.log"

# Function to gracefully stop the script
stop_script() {
    echo "$(date): Stopping script..." | tee -a "$LOG_FILE"
    if [ -f "$CONTROL_FILE" ]; then
        rm "$CONTROL_FILE"
    fi
    if [ -f "$LOG_FILE" ]; then
        rm "$LOG_FILE"
    fi
    exit 0
}

# Setting up the trap to capture SIGINT (Ctrl+C) and stop the script
trap stop_script SIGINT

# Starting the log
echo "$(date): Starting script..." | tee "$LOG_FILE"

# Infinite loop to keep the window active
while true; do
    echo "$(date): Checking for stop file..." | tee -a "$LOG_FILE"

    # Checking if the control file exists to stop the script
    if [ -f "$CONTROL_FILE" ]; then
        echo "$(date): Stop file found. Stopping script..." | tee -a "$LOG_FILE"
        stop_script
    fi

    # Search for the MS Teams window
    WINDOW_ID=$(xdotool search --name "$WINDOW_NAME" | head -n 1)

    # If the window is found, interact with it
    if [ -n "$WINDOW_ID" ]; then
        echo "$(date): Interacting with window..." | tee -a "$LOG_FILE"
        # Simulate mouse movement
        xdotool mousemove --window "$WINDOW_ID" 100 100
        xdotool mousemove --window "$WINDOW_ID" 200 200
    else
        echo "$(date): Window not found!" | tee -a "$LOG_FILE"
    fi

    # Wait for the defined interval
    sleep "$INTERVAL"
done

