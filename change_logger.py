import datetime
import os

# This global variable will be updated by `configure_log_file_path`
LOG_FILE_PATH = None

def configure_log_file_path(log_file_path: str):
    """Sets the path for the change log file."""
    global LOG_FILE_PATH
    LOG_FILE_PATH = log_file_path

def log_change(file_path: str, change_description: str):
    global LOG_FILE_PATH # Ensure we are using the global variable
    if LOG_FILE_PATH is None:
        print("Error: Log file path not configured. Call configure_log_file_path first.")
        # Fallback to a default local log file to prevent errors if not configured
        current_dir_log_path = os.path.join(os.getcwd(), "unconfigured_change_log.txt")
        print(f"Logging to default path: {current_dir_log_path}")
        LOG_FILE_PATH = current_dir_log_path


    """Appends a timestamp, file path, and change description to the log file."""
    try:
        # Ensure the directory for the log file exists
        log_dir = os.path.dirname(LOG_FILE_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        with open(LOG_FILE_PATH, "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp} - FILE: {file_path} - CHANGE: {change_description}\n"
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to change log: {e}")

def get_change_history(file_path: str) -> list[str]:
    """Reads the log file and returns a list of changes relevant to the given file_path."""
    history = []
    try:
        if not os.path.exists(LOG_FILE_PATH):
            return history

        with open(LOG_FILE_PATH, "r") as f:
            for line in f:
                if f"FILE: {file_path}" in line:
                    history.append(line.strip())
    except Exception as e:
        print(f"Error reading from change log: {e}")
    return history

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    configure_log_file_path("test_change_log.txt") # Use a test log file

    log_change("example/file1.txt", "Initial version created.")
    log_change("example/file2.txt", "Added new feature X.")
    log_change("example/file1.txt", "Fixed bug Y in file1.")

    print("\nChange history for example/file1.txt:")
    for entry in get_change_history("example/file1.txt"):
        print(entry)

    print("\nChange history for example/file2.txt:")
    for entry in get_change_history("example/file2.txt"):
        print(entry)

    # Clean up the test log file
    if os.path.exists("test_change_log.txt"):
        os.remove("test_change_log.txt")
