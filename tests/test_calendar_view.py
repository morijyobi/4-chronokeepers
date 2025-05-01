import unittest
import tkinter as tk
from unittest.mock import MagicMock
from app.calendar_view import CalendarView

class TestCalendarView(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.switch_frame_mock = MagicMock()

    def test_create_widgets(self):
        view = CalendarView(self.root, self.switch_frame_mock, test_mode=True)
        self.assertIsNotNone(view.pen_button)

    def test_button_click(self):
        view = CalendarView(self.root, self.switch_frame_mock, test_mode=True)
        view.cal.get_date = MagicMock(return_value="2025-04-29")        
        view.pen_button.invoke()
        self.switch_frame_mock.assert_called_once_with("write", "2025-04-29")
if __name__ == "__main__":
    unittest.main()