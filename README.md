# Keep Microsoft Teams Active

This script keeps the Microsoft Teams window active by simulating mouse movements periodically. It checks for the presence of a specific window and performs simulated movements while the window is open. It also includes additional functionalities like adjusting the time interval between movements, pausing or stopping the script, and viewing logs.

## Dependencies

- **xdotool**: Command-line tool used to simulate mouse and keyboard inputs.

### Installing xdotool

On Debian-based systems, like Ubuntu, you can install xdotool with:

```bash
sudo apt-get install xdotool
```

## Features

- **Continuous Microsoft Teams Activation**: Simulates mouse movements in the Teams window to prevent inactive status.
- **Execution Control**: Allows pausing, resuming, and stopping the script.
- **Adjustable Interval**: Modify the interval between mouse movements.
- **Log Display**: View logs to monitor the script’s activity.

## Usage

1. Save the script to a file, for example, `keep_active.py`.
2. Make the script executable (optional):
    ```bash
    chmod +x keep_active.py
    ```
3. Run the script:
    ```bash
    ./keep_active.py
    ```

## Menu Controls

The script displays an interactive menu with the following options:

1. **Start Script**: Begins keeping the Microsoft Teams window active.
2. **Stop Script**: Creates a control file to stop the script.
3. **Display Logs**: Shows the current log content.
4. **Modify Interval**: Allows changing the time interval between mouse movements.
5. **Pause/Resume Script**: Pauses or resumes the script.
6. **Exit**: Exits the script.

## Files and Logs

- **Control File**: `/tmp/stop_keep_active` – a file that, when created, stops the script.
- **Log File**: `/tmp/keep_active.log` – logs key events for monitoring.

## Code Structure

- **Main Function**: `start_script()` – Monitors and interacts with the Teams window.
- **Interaction Functions**: `find_window_id()` finds the Teams window, and `interact_with_window()` simulates mouse movements.
- **Signal Handling**: `stop_script()` stops the script and cleans up temporary files.
- **Interactive Menu**: The `menu()` function displays options and enables control over script execution.

## License

This script is licensed under the [MIT License](LICENSE).
