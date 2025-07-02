import unittest
import os
import datetime
from change_logger import log_change, get_change_history, configure_log_file_path

class TestChangeLogger(unittest.TestCase):

    TEST_LOG_FILE = "test_temp_change_log.txt"
    FILE_PATH_1 = "test/file1.txt"
    FILE_PATH_2 = "test/module/file2.py"

    def setUp(self):
        """Configure a temporary log file for testing and ensure it's clean."""
        configure_log_file_path(self.TEST_LOG_FILE)
        # Clean up the test log file before each test if it exists
        if os.path.exists(self.TEST_LOG_FILE):
            os.remove(self.TEST_LOG_FILE)

    def tearDown(self):
        """Clean up the test log file after all tests."""
        if os.path.exists(self.TEST_LOG_FILE):
            os.remove(self.TEST_LOG_FILE)

    def test_log_change_creates_file(self):
        """Test that log_change creates the log file if it doesn't exist."""
        self.assertFalse(os.path.exists(self.TEST_LOG_FILE))
        log_change(self.FILE_PATH_1, "First log entry.")
        self.assertTrue(os.path.exists(self.TEST_LOG_FILE))

    def test_log_change_writes_correct_format(self):
        """Test that log_change writes entries in the expected format."""
        description = "Test change description with special characters: !@#$%^&*()"
        log_change(self.FILE_PATH_1, description)

        with open(self.TEST_LOG_FILE, "r") as f:
            content = f.read()

        # Check for timestamp (format YYYY-MM-DD HH:MM:SS)
        # We don't check the exact time, just the pattern
        self.assertRegex(content, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
        self.assertIn(f"FILE: {self.FILE_PATH_1}", content)
        self.assertIn(f"CHANGE: {description}", content)
        self.assertTrue(content.endswith("\n"))

    def test_log_multiple_changes(self):
        """Test logging multiple changes for different files."""
        log_change(self.FILE_PATH_1, "Change A for file1")
        log_change(self.FILE_PATH_2, "Change B for file2")
        log_change(self.FILE_PATH_1, "Change C for file1")

        with open(self.TEST_LOG_FILE, "r") as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 3)
        self.assertIn(f"FILE: {self.FILE_PATH_1} - CHANGE: Change A for file1", lines[0])
        self.assertIn(f"FILE: {self.FILE_PATH_2} - CHANGE: Change B for file2", lines[1])
        self.assertIn(f"FILE: {self.FILE_PATH_1} - CHANGE: Change C for file1", lines[2])

    def test_get_change_history_empty_file(self):
        """Test get_change_history returns an empty list if the log file doesn't exist or is empty."""
        # Test before file is created
        self.assertEqual(get_change_history(self.FILE_PATH_1), [])
        # Test with an empty file
        open(self.TEST_LOG_FILE, 'w').close() # Create empty file
        self.assertEqual(get_change_history(self.FILE_PATH_1), [])

    def test_get_change_history_filters_correctly(self):
        """Test that get_change_history returns only entries for the specified file_path."""
        log_change(self.FILE_PATH_1, "File1-Update1")
        log_change(self.FILE_PATH_2, "File2-Update1")
        log_change(self.FILE_PATH_1, "File1-Update2")
        log_change("another/file.txt", "OtherFile-Update")

        history_file1 = get_change_history(self.FILE_PATH_1)
        self.assertEqual(len(history_file1), 2)
        self.assertIn("File1-Update1", history_file1[0])
        self.assertIn("File1-Update2", history_file1[1])

        history_file2 = get_change_history(self.FILE_PATH_2)
        self.assertEqual(len(history_file2), 1)
        self.assertIn("File2-Update1", history_file2[0])

        history_other = get_change_history("another/file.txt")
        self.assertEqual(len(history_other), 1)
        self.assertIn("OtherFile-Update", history_other[0])

    def test_get_change_history_no_matching_entries(self):
        """Test get_change_history returns an empty list if no entries match the file_path."""
        log_change(self.FILE_PATH_1, "Some change for file1")
        log_change(self.FILE_PATH_2, "Some change for file2")

        history_nonexistent = get_change_history("nonexistent/path.txt")
        self.assertEqual(history_nonexistent, [])

    def test_log_entry_timestamp_accuracy(self):
        """Test that the timestamp is close to the current time."""
        # This test has a small chance of failing if system clock changes or execution is extremely slow
        # between these two lines, but generally it should pass.
        time_before_log = datetime.datetime.now()
        log_change(self.FILE_PATH_1, "Timestamp test")
        time_after_log = datetime.datetime.now()

        with open(self.TEST_LOG_FILE, "r") as f:
            log_line = f.readline().strip()

        timestamp_str = log_line.split(" - ")[0]
        log_timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

        # Allow a small delta (e.g., 5 seconds) for processing time
        # This accounts for potential delays in file I/O or test execution environments
        self.assertTrue(time_before_log - datetime.timedelta(seconds=1) <= log_timestamp <= time_after_log + datetime.timedelta(seconds=5))

if __name__ == '__main__':
    unittest.main()
