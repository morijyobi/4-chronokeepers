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

    @patch("app.write_view.configure")  # ←ここを変更！
    @patch("app.write_view.GenerativeModel")  # ←ここを変更！    
    def test_save_diary_creates_files(self, MockModel, mock_configure):
        # configureの呼び出しをモックしてAPIキー設定を無効にする
        mock_configure.return_value = None  # configureメソッドを完全にモックしてAPIキー設定を無効にする

        # モックの戻り値設定
        mock_instance = MockModel.return_value
        mock_instance.generate_content.return_value.text = "モックのコメントです"

        # save_diaryを実行
        self.app.save_diary()

        # CSVファイルが存在しているか確認
        self.assertTrue(os.path.exists(self.app.filepath))
        with open(self.app.filepath, encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], self.date)

        # テキストファイルが存在しているか確認
        self.assertTrue(os.path.exists(self.app.txtpath))
        with open(self.app.txtpath, encoding='utf-8') as f:
            content = f.read()
            self.assertIn("これはテストの日記です。", content)
    @patch("app.write_view.configure")  # ←ここを変更！
    @patch("app.write_view.GenerativeModel")  # ←ここを変更！    
    @patch("app.write_view.messagebox.showinfo")
    def test_teach_diary_calls_messagebox(self, mock_showinfo, mock_configure, MockModel):
        # configureの呼び出しをモックしてAPIキー設定を無効にする
        mock_configure.return_value = None  # configureメソッドを完全にモックしてAPIキー設定を無効にする

        # モックの戻り値設定
        mock_instance = MockModel.return_value
        mock_instance.generate_content.return_value.text = "これは添削のアドバイスです。"

        # teach_diaryを実行
        self.app.teach_diary()

        # messagebox.showinfoが呼ばれたか確認
        mock_showinfo.assert_called_once()
        args = mock_showinfo.call_args[0]
        self.assertIn("ジェミニ先生からのアドバイス", args[1])
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