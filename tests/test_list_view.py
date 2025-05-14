import unittest
import tkinter as tk
import os
import tempfile
import csv
from app.list_view import DiaryListApp

class TestDiaryListApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

        # 一時ディレクトリとダミーファイルの作成
        self.test_dir = tempfile.mkdtemp()
        self.test_csv = os.path.join(self.test_dir, "test_diary.csv")
        self.test_text_dir = os.path.join(self.test_dir, "texts")
        os.makedirs(self.test_text_dir)

        # ダミーのCSVファイル作成
        with open(self.test_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["2025-05-01", "0", "80", "1"])

        # ダミーのテキストファイル作成
        with open(os.path.join(self.test_text_dir, "2025-05-01.txt"), "w", encoding="utf-8") as f:
            f.write("これはサンプルの日記です。")

        # パスを差し替え
        self.original_csv = DiaryListApp.__dict__["read_csv_entries"]
        self.original_txt = DiaryListApp.__dict__["read_txt_entries"]

        DiaryListApp.read_csv_entries = lambda self: [{
            "日付": "2025-05-01", "天気": "0", "充実度": "80", "行動": "1"
        }]
        DiaryListApp.read_txt_entries = lambda self: [{
            "日付": "2025-05-01", "本文": "これはサンプルの日記です。"
        }]

        # テスト対象インスタンス作成
        self.app = DiaryListApp(self.root, lambda x: x)

    def tearDown(self):
        self.app.destroy()
        self.root.destroy()
        DiaryListApp.read_csv_entries = self.original_csv
        DiaryListApp.read_txt_entries = self.original_txt

    def test_diary_tree_inserts_data(self):
        items = self.app.diary_tree.get_children()
        self.assertEqual(len(items), 1)
        first = self.app.diary_tree.item(items[0])['values']
        self.assertEqual(first[0], "2025-05-01")
        self.assertIn("晴れ", first[1])  # 天気コード0 = 晴れ

    def test_text_tree_inserts_data(self):
        items = self.app.text_tree.get_children()
        self.assertEqual(len(items), 1)
        first = self.app.text_tree.item(items[0])['values']
        self.assertEqual(first[0], "2025-05-01")
        self.assertTrue("..." in first[1] or "これはサンプルの日記です。" in first[1])

if __name__ == '__main__':
    unittest.main()