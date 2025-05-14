import unittest
import tkinter as tk
import tempfile
import shutil
import os
import csv
from unittest.mock import MagicMock, patch
from app.write_view import DiaryApp

class TestDiaryApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

        # テスト用の一時フォルダを作成
        self.test_dir = tempfile.mkdtemp()
        self.test_text_dir = os.path.join(self.test_dir, "texts")
        os.makedirs(self.test_text_dir)

        self.date = "2025-05-07"
        self.app = DiaryApp(self.root, self.date, lambda x: x)
        
        # 保存先パスをテスト用ディレクトリに変更
        self.app.folder = self.test_dir
        self.app.textfold = self.test_text_dir
        self.app.filename = "test_diary.csv"
        self.app.textfile = f"{self.date}.txt"
        self.app.filepath = os.path.join(self.test_dir, self.app.filename)
        self.app.txtpath = os.path.join(self.test_text_dir, self.app.textfile)

        # 入力データを設定
        self.app.slider.set(80)
        self.app.weather_combo.set("晴れ☀")
        self.app.action_combo.set("出社")
        self.app.text.insert("1.0", "これはテストの日記です。")

    def tearDown(self):
        # まずウィンドウが完全にイベントを処理できる状態で終了
        self.app.quit()  # Tkinterのイベントループを終了
        self.app.destroy()  # 破棄処理
        self.root.quit()  # Tkinterのイベントループを終了
        self.root.destroy()  # 破棄処理
        shutil.rmtree(self.test_dir)  # テスト用ディレクトリを削除

    @patch('app.write_view.messagebox.showinfo')
    def test_save_diary_creates_files(self, mock_showinfo):
        os.makedirs(os.path.dirname(self.app.filepath), exist_ok=True)

        # ダミーのデータを渡す（内容はなんでもよい）
        self.app._perform_save(
            fulfillment_val="5",
            weather_key="晴れ",
            action_key="休日",
            content_text="テスト日記",
            weather_val_csv="sunny",
            action_val_csv="study"
        )

        self.assertTrue(os.path.exists(self.app.filepath))

    @patch('app.write_view.messagebox.showinfo')
    @patch.object(tk.Tk, 'after', lambda self, time_ms, func, *args: func(*args))  # afterを即実行に
    def test_teach_diary_calls_messagebox(self, mock_showinfo):
        # イベントで同期を取る
        import threading
        called_event = threading.Event()

        # showinfo をフックして、呼び出されたらイベントをセット
        def on_showinfo(*args, **kwargs):
            called_event.set()

        mock_showinfo.side_effect = on_showinfo

        # 添削処理を開始
        self.app._perform_teach(
            fulfillment_val="3",
            weather_key="曇り",
            action_key="運動",
            content_text="今日はちょっとだけ体を動かした。"
        )

        # 最大5秒まで待機
        called = called_event.wait(timeout=5)

        self.assertTrue(called, "messagebox.showinfo was not called within timeout")
    def test_limit_text_length_does_not_cut_short_text(self):
        # 200文字以内のテキスト
        short_text = "短いテキストです。" * 10  # 約100文字程度
        self.app.text.delete("1.0", tk.END)
        self.app.text.insert("1.0", short_text)

        event = MagicMock()
        event.widget = self.app.text

        self.app.limit_text_length(event)

        current_text = self.app.text.get("1.0", "end-1c")
        self.assertEqual(current_text, short_text)

    def test_limit_text_length_cuts_long_text(self):
        long_text = "あ" * 250  # 250文字の長文
        self.app.text.delete("1.0", tk.END)
        self.app.text.insert("1.0", long_text)

        event = MagicMock()
        event.widget = self.app.text

        self.app.limit_text_length(event)

        current_text = self.app.text.get("1.0", "end-1c")
        self.assertEqual(len(current_text), 200)
        self.assertTrue(current_text.startswith("あ" * 200))

if __name__ == "__main__":
    unittest.main()