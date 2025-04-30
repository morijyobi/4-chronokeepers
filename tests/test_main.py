import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk

# Mainクラスをインポート
from main import Main

class TestMain(unittest.TestCase):
    def setUp(self):
        # Tkinterのウィンドウを実際には開かないようにする
        self.app = Main()
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    @patch('main.CalendarView')
    def test_switch_to_calendar(self, MockCalendarView):
        mock_frame = MagicMock()
        MockCalendarView.return_value = mock_frame

        self.app.switch_frame("calendar")

        MockCalendarView.assert_called_once_with(self.app, self.app.switch_frame)
        mock_frame.pack.assert_called_once()

    @patch('main.DiaryApp')
    def test_switch_to_write(self, MockDiaryApp):
        mock_frame = MagicMock()
        MockDiaryApp.return_value = mock_frame

        self.app.switch_frame("write", date="2025-04-29")

        MockDiaryApp.assert_called_once_with(self.app, "2025-04-29", self.app.switch_frame)
        mock_frame.pack.assert_called_once()

    @patch('main.ListView')
    def test_switch_to_list(self, MockListView):
        mock_frame = MagicMock()
        MockListView.return_value = mock_frame

        self.app.switch_frame("list")

        MockListView.assert_called_once_with(self.app, self.app.switch_frame)
        mock_frame.pack.assert_called_once()

if __name__ == "__main__":
    unittest.main()