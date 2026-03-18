import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Create mock modules for ALL dependencies that might be missing in the test environment
mock_modules = [
    'matplotlib', 'matplotlib.pyplot', 'matplotlib.animation',
    'matplotlib.backends.backend_tkagg', 'numpy', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox'
]
for module_name in mock_modules:
    sys.modules[module_name] = MagicMock()

# Manually create the TelemetryApp class from its source,
# but only the bits we need, or execute it in a carefully prepared namespace.
def get_telemetry_app_class():
    # Use absolute path or path relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "DASHBOARDpython.txt")

    with open(file_path, "r") as f:
        content = f.read()

    # We want to execute the class definition in a controlled namespace
    namespace = {
        'tk': MagicMock(),
        'ttk': MagicMock(),
        'messagebox': MagicMock(),
        'socket': MagicMock(),
        'threading': MagicMock(),
        'deque': MagicMock(),
        'time': MagicMock(),
        'np': MagicMock(),
        'FuncAnimation': MagicMock(),
        'FigureCanvasTkAgg': MagicMock(),
        'plt': MagicMock(),
        'filedialog': MagicMock(),
        'UDP_IP': "127.0.0.1",
        'UDP_PORT': 4444,
        'BUFFER_SIZE': 1024,
        'VIEW_POINTS': 100,
        'RATE_SCALE': 0.25,
        'LAUNCHER_GATEWAY': "192.168.4.1"
    }

    try:
        # Wrap in a way that avoids top-level side effects if possible
        # but the DASHBOARDpython.txt has if __name__ == "__main__": so it should be fine
        exec(content, namespace)
    except Exception as e:
        print(f"Warning: exec(content) encountered an error: {e}")

    return namespace.get('TelemetryApp'), namespace.get('messagebox')

TelemetryAppClass, mock_messagebox = get_telemetry_app_class()

class TestSendPidCommand(unittest.TestCase):
    def setUp(self):
        if TelemetryAppClass is None:
            self.fail("Could not load TelemetryApp class")

        # Patch __init__ to avoid full GUI and thread initialization
        with patch.object(TelemetryAppClass, '__init__', return_value=None):
            self.app = TelemetryAppClass(None)
            # Manually set up the minimal state needed for send_pid_command
            self.app.kp_var = MagicMock()
            self.app.kd_var = MagicMock()
            self.app._send_udp_command = MagicMock()

    def test_send_pid_command_value_error(self):
        # Configure mocks to trigger ValueError when calling float()
        self.app.kp_var.get.return_value = "not_a_float"
        self.app.kd_var.get.return_value = "0.2"

        # Reset mock_messagebox before call
        mock_messagebox.showerror.reset_mock()

        # Call the method
        self.app.send_pid_command()

        # Verify error was shown and command was NOT sent
        mock_messagebox.showerror.assert_called_once_with("Error", "Kp and Kd must be valid numbers.")
        self.app._send_udp_command.assert_not_called()

    def test_send_pid_command_valid_input(self):
        # Reset mock_messagebox and _send_udp_command
        mock_messagebox.showerror.reset_mock()
        self.app._send_udp_command.reset_mock()

        # Configure mocks for valid input
        self.app.kp_var.get.return_value = "0.5"
        self.app.kd_var.get.return_value = "0.2"

        # Call the method
        self.app.send_pid_command()

        # Verify command WAS sent and NO error shown
        self.app._send_udp_command.assert_called_once_with("PID,0.5,0.2")
        mock_messagebox.showerror.assert_not_called()

if __name__ == "__main__":
    unittest.main()
