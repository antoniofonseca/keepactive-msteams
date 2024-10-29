#!/usr/bin/env python3
"""
Script to keep the Microsoft Teams window active.

This script continuously checks for a window with a specific name (Microsoft Teams) 
and simulates mouse movements to keep the window active. It also checks for the 
existence of a control file to gracefully stop the script.

Dependencies:
- xdotool: Command-line tool to simulate mouse and keyboard inputs.

Installing dependencies:
For Debian-based systems (like Ubuntu), you can install xdotool with the following command:
    sudo apt-get install xdotool

Usage:
1. Save this script to a file, for example, `keep_active.py`.
2. Make the script executable (optional):
    chmod +x keep_active.py
3. Run the script:
    ./keep_active.py
"""

import os
import time
import signal
import logging
import subprocess
import sys
import curses
import threading
from datetime import datetime, timedelta
from random import randint

# Constants
WINDOW_NAME = "Microsoft Teams"
DEFAULT_INTERVAL = 300  # Default to 5 minutes
CONTROL_FILE = "/tmp/stop_keep_active"
LOG_FILE = "/tmp/keep_active.log"

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

is_running = False
is_paused = False
interval = DEFAULT_INTERVAL
start_time = None
paused_time = None

# Check for xdotool dependency
try:
    subprocess.run(['xdotool', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except FileNotFoundError:
    print("Error: xdotool is not installed. Please install it using 'sudo apt-get install xdotool'")
    sys.exit(1)

def find_window_id(window_name):
    """Find the window ID for the given window name using xdotool."""
    try:
        result = subprocess.run(
            ['xdotool', 'search', '--name', window_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        window_id = result.stdout.strip().split('\n')[0]
        return window_id
    except subprocess.CalledProcessError:
        return None

def interact_with_window(window_id):
    """Simulate mouse movement within the given window with randomization."""
    x = randint(50, 250)
    y = randint(50, 250)
    subprocess.run(['xdotool', 'mousemove', '--window', window_id, str(x), str(y)], check=True)
    logging.info("Interacting with window ID %s at (%d, %d)", window_id, x, y)

def stop_script(signum=None, frame=None):
    """Gracefully stop the script and clean up."""
    global is_running
    logging.info("Stopping script...")
    is_running = False
    cleanup_files()
    sys.exit(0)

def cleanup_files():
    """Remove control and log files."""
    for file_path in [CONTROL_FILE, LOG_FILE]:
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                logging.info("Removed %s", file_path)
            except OSError as e:
                logging.error("Error removing %s: %s", file_path, e)

# Set up signal handler to catch SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, stop_script)

def display_log(stdscr):
    """Display the current log content and wait for user input to return to the menu."""
    stdscr.clear()

    log_content = []  # Initialize log_content to an empty list
    if not os.path.exists(LOG_FILE):
        stdscr.addstr(0, 0, "Log file does not exist. No logs to display.")
    else:
        with open(LOG_FILE, 'r') as f:
            log_content = f.readlines()
        for i, line in enumerate(log_content):
            stdscr.addstr(i, 0, line.strip())

    stdscr.addstr(len(log_content) + 1, 0, "\nPress Enter to return to the menu...")
    stdscr.refresh()
    stdscr.getch()

def modify_interval(stdscr):
    """Modify the interval time with input validation, preventing changes while running or paused."""
    global interval
    if is_running or is_paused:
        stdscr.clear()
        stdscr.addstr(0, 0, "Cannot modify interval while the script is running or paused.")
        stdscr.addstr(1, 0, "Please stop or resume the script before changing the interval.")
    else:
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter new interval time in seconds (positive integer): ")
        curses.echo()
        new_interval_str = stdscr.getstr(1, 0, 10).decode('utf-8')
        curses.noecho()
        try:
            new_interval = int(new_interval_str)
            if new_interval > 0:
                interval = new_interval
                stdscr.addstr(2, 0, f"Interval set to {interval} seconds.")
            else:
                stdscr.addstr(2, 0, "Invalid input. Interval must be a positive integer.")
        except ValueError:
            stdscr.addstr(2, 0, "Invalid input. Interval not changed.")
    stdscr.addstr(3, 0, "\nPress Enter to return to the menu...")
    stdscr.refresh()
    stdscr.getch()

def start_script(stdscr):  # No `self` argument here
    """Start the script to keep the MS Teams window active."""
    global is_running, interval, start_time
    logging.info("Starting script...")
    is_running = True
    start_time = datetime.now()  # Reset start_time when starting

    while is_running and not os.path.isfile(CONTROL_FILE):
        logging.info("Checking for stop file...")

        # If the script is paused, wait until it's resumed
        while is_paused:
            time.sleep(1)

        # Search for the MS Teams window
        window_id = find_window_id(WINDOW_NAME)

        # If the window is found, interact with it
        if window_id:
            interact_with_window(window_id)
        else:
            logging.info("Window not found!")

        # Wait for the defined interval
        for _ in range(interval):
            if not is_running or os.path.isfile(CONTROL_FILE):
                break
            time.sleep(1)

    logging.info("Stop file found or script stopped. Stopping script...")
    stop_script(None, None)

def get_elapsed_time():
    """Get the elapsed time since the script started, accounting for pauses."""
    global paused_time
    if not start_time:
        return "N/A"

    current_time = datetime.now()
    elapsed_time = current_time - start_time

    if paused_time:
        elapsed_time -= current_time - paused_time
    return str(elapsed_time).split('.')[0]  # Return in HH:MM:SS format

def update_elapsed_time(stdscr):
    """Update the elapsed time in the UI."""
    while True:  # Run indefinitely
        if is_running:  # Update only when the script is running
            elapsed_time_str = get_elapsed_time()
            stdscr.addstr(11, 0, f"Elapsed Time: {elapsed_time_str}")
            stdscr.refresh()
        time.sleep(1)

def menu(stdscr):
    """Display a simple text-based menu for user interaction."""
    global is_running, interval, is_paused, paused_time, elapsed_time_before_pause
    curses.curs_set(0)

    # Start the elapsed time updater thread
    elapsed_time_thread = threading.Thread(target=update_elapsed_time, args=(stdscr,), daemon=True)
    elapsed_time_thread.start()

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Choose an action:")
        stdscr.addstr(1, 0, "1. Start Script - Begin the process to keep the MS Teams window active.")
        stdscr.addstr(2, 0, "2. Stop Script - Stop the script by creating the control file.")
        stdscr.addstr(3, 0, "3. Display Log - Show the current log content.")
        stdscr.addstr(4, 0, "4. Modify Interval - Change the interval time in seconds.")
        stdscr.addstr(5, 0, "5. Pause/Resume Script - Pause or resume the script.")
        stdscr.addstr(6, 0, "6. Exit - Exit the script.")

        # Determine the current status string
        if is_paused and is_running:
            status_str = "Running (Paused)"
        elif is_running:
            status_str = "Running"
        else:
            status_str = "Stopped"  # Prioritize "Stopped" when not running

        stdscr.addstr(8, 0, f"Current Status: {status_str}")
        stdscr.addstr(9, 0, f"Current Interval: {interval} seconds")
        stdscr.addstr(11, 0, f"Elapsed Time: {get_elapsed_time()}")

        stdscr.refresh()

        choice = stdscr.getch()

        if choice == ord('1'):
            if is_running:
                stdscr.addstr(12, 0, "The script is already running.")
            else:
                stdscr.addstr(12, 0, "Starting script...")
                stdscr.refresh()
                threading.Thread(target=start_script, args=(stdscr,)).start()

        elif choice == ord('2'):
            if not is_running:
                stdscr.addstr(12, 0, "The script is not running.")
            else:
                with open(CONTROL_FILE, 'w') as f:
                    pass
                stdscr.addstr(12, 0, "Stop file created. Script will stop soon.")
            stdscr.refresh()
            time.sleep(2)

        elif choice == ord('3'):
            display_log(stdscr)

        elif choice == ord('4'):
            modify_interval(stdscr)

        elif choice == ord('5'):
            if is_running:
                is_paused = not is_paused
                if is_paused:
                    paused_time = datetime.now()
                else:
                    paused_time = None
                stdscr.addstr(12, 0, f"Script {'paused' if is_paused else 'resumed'}.")
            else:
                stdscr.addstr(12, 0, "Script is not running. Cannot pause/resume.")
            stdscr.refresh()
            time.sleep(2)

        elif choice == ord('6'):
            if is_running:
                stdscr.addstr(12, 0, "The script is running. Please stop it first.")
                stdscr.addstr(13, 0, "Press 's' to stop and exit, or any other key to return to the menu.")
                stdscr.refresh()
                confirm_exit = stdscr.getch()
                if confirm_exit == ord('s'):
                    with open(CONTROL_FILE, 'w') as f:
                        pass
                    stdscr.addstr(14, 0, "Stop file created. Script will stop soon.")
                    is_running = False
                    stdscr.refresh()
                    time.sleep(2)
                    stop_script(None, None) # Stop the main script
                    elapsed_time_thread.join()  # Wait for the elapsed time thread to finish
                    break  # Exit the menu loop
            else:
                stdscr.addstr(12, 0, "Exiting. The script will stop.")
                stdscr.refresh()
                time.sleep(2)
                stop_script(None, None)  # Stop the main script
                elapsed_time_thread.join()  # Wait for the elapsed time thread to finish
                break  # Exit the menu loop

        else:
            stdscr.addstr(12, 0, "Invalid choice. Please try again.")
            stdscr.refresh()
            time.sleep(2)

if __name__ == "__main__":
    curses.wrapper(menu)
