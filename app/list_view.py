import tkinter as tk
from tkinter import ttk
import csv
import os
from datetime import datetime

class DiaryListApp(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        # ウィンドウの設定
        master.geometry('400x400')
        master.title('日記一覧')
        
        # スクロール可能なキャンバスを作成
        self.canvas = tk.Canvas(master)
        self.scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        # スクロール可能なフレームを設定
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        # キャンバスにフレームを追加
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # キャンバスのサイズを親ウィンドウに合わせて調整
        self.canvas.bind("<Configure>", self.resize_canvas)
        
        # キャンバスとスクロールバーを配置
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # キャンバスとスクロールバーを連動
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # このフレームを scrollable_frame に配置
        self.inner_frame = tk.Frame(self.scrollable_frame)
        self.inner_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()
        self.load_diary_data()
        
        # マウスホイールでスクロールを可能にする
        # self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def resize_canvas(self, event):
        # キャンバスのサイズを親ウィンドウに合わせて調整
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def _on_mousewheel(self, event):
        # Windowsの場合
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_widgets(self):
        # ヘッダーフレーム
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X)
        
        # メニューバー
        menubar = tk.Menu(self.master)
        self.master.configure(menu=menubar)
        diary_menu = tk.Menu(menubar, tearoff=0)
        
        menubar.add_cascade(label='日記メニュー', menu=diary_menu)
        
        diary_menu.add_command(label='日記作成', command=self.diary_write)
        diary_menu.add_command(label='日記一覧', command=self.diary_list)
        
        # CSVヘッダー情報
        csv_info_label = ttk.Label(self.scrollable_frame, text="CSV日付、天気、充実度、行動", font=('Helvetica', 10, 'bold'))
        csv_info_label.pack(pady=(10, 5))  # 上部に10px、下部に5pxの余白
        
        # CSV表示用のTreeviewフレーム（スクロールバー付き）
        diary_frame = ttk.Frame(self.scrollable_frame)
        diary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 上部テーブル用の垂直スクロールバー
        diary_scrolly = ttk.Scrollbar(diary_frame, orient="vertical")
        diary_scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 上部テーブル用の水平スクロールバー
        diary_scrollx = ttk.Scrollbar(diary_frame, orient="horizontal")
        diary_scrollx.pack(side=tk.BOTTOM, fill=tk.X)
        
        # CSV表示用のTreeview（上部テーブル）- スクロールバーと連動
        self.diary_tree = ttk.Treeview(diary_frame, columns=('date', 'weather', 'fulfillment', 'action'), 
                                        show='headings', height=3,
                                        yscrollcommand=diary_scrolly.set,
                                        xscrollcommand=diary_scrollx.set)
        
        # スクロールバーとTreeviewを連動
        diary_scrolly.config(command=self.diary_tree.yview)
        diary_scrollx.config(command=self.diary_tree.xview)
        
        self.diary_tree.heading('date', text='日付')
        self.diary_tree.heading('weather', text='天気')
        self.diary_tree.heading('fulfillment', text='充実度')
        self.diary_tree.heading('action', text='行動')
        
        self.diary_tree.column('date', width=100)
        self.diary_tree.column('weather', width=50)
        self.diary_tree.column('fulfillment', width=50)
        self.diary_tree.column('action', width=50)
        
        self.diary_tree.pack(fill=tk.BOTH, expand=True)
        
        # テキスト（日付、本文）ラベル
        text_label = ttk.Label(self.scrollable_frame, text="テキスト(日付、本文)", font=('Helvetica', 10, 'bold'))
        text_label.pack(padx=(0,33), pady=(10, 5))  # 上部に10px、下部に5pxの余白   # 右に33pxの余白を追加
        
        explanation_label = tk.Label(self.scrollable_frame, text="※ダブルクリックで詳細表示",font=('HGPｺﾞｼｯｸM', 8))
        explanation_label.place(x=247, y=165) # 説明文を追加
        
        # テキスト表示用のTreeviewフレーム（スクロールバー付き）
        text_frame = ttk.Frame(self.scrollable_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 下部テーブル用の垂直スクロールバー
        text_scrolly = ttk.Scrollbar(text_frame, orient="vertical")
        text_scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 下部テーブル用の水平スクロールバー
        text_scrollx = ttk.Scrollbar(text_frame, orient="horizontal")
        text_scrollx.pack(side=tk.BOTTOM, fill=tk.X)
        
        # テキスト表示用のTreeview（下部テーブル）- スクロールバーと連動
        self.text_tree = ttk.Treeview(text_frame, columns=('date', 'content'), 
                                      show='headings', height=10,
                                      yscrollcommand=text_scrolly.set,
                                      xscrollcommand=text_scrollx.set)
        
        # スクロールバーとTreeviewを連動
        text_scrolly.config(command=self.text_tree.yview)
        text_scrollx.config(command=self.text_tree.xview)
        
        self.text_tree.heading('date', text='日付')
        self.text_tree.heading('content', text='本文')
        
        self.text_tree.column('date', width=100)
        self.text_tree.column('content', width=300)  # 少し幅を調整
        self.text_tree.pack(fill=tk.BOTH, expand=True)
    
    def load_diary_data(self):
        self.load_from_csv()
    
    def load_from_csv(self):
        # CSVファイルのディレクトリ
        csv_dir = "./data/"
        
        # ディレクトリが存在しない場合は作成
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
            print(f"ディレクトリを作成しました: {csv_dir}")
            # サンプルデータを追加
            self.diary_tree.insert('', 'end', values=('2025.04.20', '2', '80', '2'))
            self.text_tree.insert('', 'end', values=('2025.04.20', '今日は晴れて日記を書くのを忘れた。'))
            return
        
        # CSVファイルが見つからない場合はサンプルデータを表示
        files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
        if not files:
            print("CSVファイルが見つかりません。サンプルデータを表示します。")
            self.diary_tree.insert('', 'end', values=('2025.04.20', '2', '80', '2'))
            self.text_tree.insert('', 'end', values=('2025.04.20', '今日は晴れて日記を書くのを忘れた。'))
            return
        
        # ディレクトリ内のCSVファイルを読み込む
        for filename in files:
            file_path = os.path.join(csv_dir, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    # ヘッダー行があれば読み飛ばす
                    try:
                        headers = next(reader)
                    except StopIteration:
                        print(f"空のCSVファイル: {file_path}")
                        continue
                    
                    for row in reader:
                        if len(row) >= 4:  # 必要なデータがある場合
                            date_str = row[0]
                            weather = row[1]
                            fulfillment = row[2]
                            action = row[3]
                            
                            # 上部テーブルに追加
                            self.diary_tree.insert('', 'end', values=(date_str, weather, fulfillment, action))
                        
                        if len(row) >= 5:  # 本文がある場合
                            date_str = row[0]
                            content = row[4]
                            
                            # 下部テーブルに追加
                            self.text_tree.insert('', 'end', values=(date_str, content))
            except Exception as e:
                print(f"ファイル読み込みエラー {file_path}: {e}")

    def diary_write(self):
        # 新規日記作成画面へ遷移する処理
        print("日記作成画面へ遷移します")
    
    def diary_list(self):
        # 現在の日記一覧画面を更新
        print("日記一覧を更新します")
        # テーブルをクリアして再読み込み
        for item in self.diary_tree.get_children():
            self.diary_tree.delete(item)
        for item in self.text_tree.get_children():
            self.text_tree.delete(item)
        self.load_diary_data()

if __name__ == '__main__':
    root = tk.Tk()
    app = DiaryListApp(root)
    root.mainloop()