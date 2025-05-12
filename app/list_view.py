import tkinter as tk
from tkinter import ttk,messagebox
import csv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(BASE_DIR, 'data', 'diary_data.csv')
TEXT_FOLDER = os.path.join(BASE_DIR, 'data', 'texts')
class DiaryListApp(tk.Frame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.switch_frame_callback = switch_frame_callback
        # ウィンドウの設定
        # self.pack(fill='both', expand=True)
        master.geometry('600x500')
        master.title('日記一覧')
        
        # スクロール可能なキャンバスを作成
        # self.canvas = tk.Canvas(self)
        # self.scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        # self.scrollable_frame = tk.Frame(self.canvas)
        
        # スクロール可能なフレームを設定
        # self.scrollable_frame.bind(
        #     "<Configure>",
        #     lambda e: self.canvas.configure(
        #         scrollregion=self.canvas.bbox("all")
        #     )
        # )
        
        # キャンバスにフレームを追加
        # self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # キャンバスのサイズを親ウィンドウに合わせて調整
        # self.canvas.bind("<Configure>", self.resize_canvas)
        # self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # キャンバスとスクロールバーを配置
        # self.canvas.pack(side="left", fill="both", expand=True)
        # self.scrollbar.pack(side="right", fill="y")
        
        # キャンバスとスクロールバーを連動
        # self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # このフレームを scrollable_frame に配置
        # self.inner_frame = tk.Frame(self.scrollable_frame)
        # self.inner_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()
        
        # マウスホイールでスクロールを可能にする
        # self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel)
    
    # def resize_canvas(self, event):
        # キャンバスのサイズを親ウィンドウに合わせて調整
        # self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    # def _on_mousewheel(self, event):
        # Windowsの場合
        # self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_widgets(self):
        self.weater_dict = {
            0: "晴れ",
            1: "曇り",
            2: "雨",
            3: "雪"
        }
        self.action_dict = {
            0: "出社",
            1: "テレワーク",
            2: "外回り",
            3: "出張",
            4: "休日"
        }

        # ヘッダーフレーム
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X)
        
        # メニューバー
        menubar = tk.Menu(self.master)
        self.master.configure(menu=menubar)
        diary_menu = tk.Menu(menubar, tearoff=0)
        
        menubar.add_cascade(label='日記メニュー', menu=diary_menu)
        
        diary_menu.add_command(label='日記作成', command=lambda: self.switch_frame_callback("calendar"))
        diary_menu.add_command(label='日記一覧', command=lambda: self.switch_frame_callback("list"))
        menubar.add_command(label='ヘルプ', command=self.push_help)
        
        # CSVヘッダー情報
        csv_info_label = ttk.Label(self, text="CSV日付、天気、充実度、行動", font=('Helvetica', 10, 'bold'))
        csv_info_label.pack(pady=(10, 5))  # 上部に10px、下部に5pxの余白
        
        # CSV表示用のTreeviewフレーム（スクロールバー付き）
        # diary_frame = ttk.Frame(self.scrollable_frame)
        # diary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 上部テーブル用の垂直スクロールバー
        # diary_scrolly = ttk.Scrollbar(diary_frame, orient="vertical")
        # diary_scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 上部テーブル用の水平スクロールバー
        # diary_scrollx = ttk.Scrollbar(diary_frame, orient="horizontal")
        # diary_scrollx.pack(side=tk.BOTTOM, fill=tk.X)
        
        # CSV表示用のTreeview（上部テーブル）- スクロールバーと連動
        self.diary_tree = ttk.Treeview(self, columns=('date', 'weather', 'fulfillment', 'action'), 
                                        show='headings', height=3) #diary_frame,yscrollcommand=diary_scrolly.set,xscrollcommand=diary_scrollx.set
        
        # スクロールバーとTreeviewを連動
        # diary_scrolly.config(command=self.diary_tree.yview)
        # diary_scrollx.config(command=self.diary_tree.xview)
        
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
        text_label = ttk.Label(self, text="テキスト(日付、本文)　※ダブルクリックで詳細表示", font=('Helvetica', 10, 'bold'))
        text_label.pack(padx=(0,33), pady=(10, 5))  # 上部に10px、下部に5pxの余白   # 右に33pxの余白を追加
        
        # テキスト表示用のTreeviewフレーム（スクロールバー付き）
        # text_frame = ttk.Frame(self.scrollable_frame)
        # text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 下部テーブル用の垂直スクロールバー
        # text_scrolly = ttk.Scrollbar(text_frame, orient="vertical")
        # text_scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 下部テーブル用の水平スクロールバー
        # text_scrollx = ttk.Scrollbar(text_frame, orient="horizontal")
        # text_scrollx.pack(side=tk.BOTTOM, fill=tk.X)
        
        # テキスト表示用のTreeview（下部テーブル）- スクロールバーと連動
        self.text_tree = ttk.Treeview(self, columns=('date', 'content'), 
                                      show='headings', height=10) #text_frame,yscrollcommand=text_scrolly.set,xscrollcommand=text_scrollx.set
        
        # スクロールバーとTreeviewを連動
        # text_scrolly.config(command=self.text_tree.yview)
        # text_scrollx.config(command=self.text_tree.xview)
        
        self.text_tree.heading('date', text='日付')
        self.text_tree.heading('content', text='本文')
        
        self.text_tree.column('date', width=100)
        self.text_tree.column('content', width=300)  # 少し幅を調整
        self.text_tree.pack(fill=tk.BOTH, expand=True)
        
        for entry in self.read_csv_entries():
            weather = self.weater_dict[int(entry["天気"])]
            action = self.action_dict[int(entry["行動"])]
            self.diary_tree.insert("", "end", values=(entry["日付"], weather, entry["充実度"], action))
        for entry in self.read_txt_entries():
            if len(entry["本文"]) > 23:
                short_body = entry["本文"][:23] + "..."
            else:
                short_body = entry["本文"]
            self.text_tree.insert("", "end", values=(entry["日付"], short_body))
        self.text_tree.bind("<Double-1>", self.on_double_click)                
    
    def read_csv_entries(self):
        entries = []

        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                entries.append({
                    "日付": row[0],
                    "天気": row[1],        # 数値のまま
                    "充実度": row[2],
                    "行動": row[3]         # 数値のまま
                })
        return entries
    def read_csv_entries(self):
        entries = []

        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                entries.append({
                    "日付": row[0],
                    "天気": row[1],        # 数値のまま
                    "充実度": row[2],
                    "行動": row[3]         # 数値のまま
                })
        return entries
    def read_txt_entries(self):
        entries = []
        if not os.path.exists(TEXT_FOLDER):
            return entries

        for filename in os.listdir(TEXT_FOLDER):
            if filename.endswith(".txt"):
                date = filename.replace(".txt", "")
                with open(os.path.join(TEXT_FOLDER, filename), "r", encoding="utf-8") as f:
                    body = f.read()
                entries.append({
                    "日付": date,
                    "本文": body
                })
        return entries
    def on_double_click(self, event):
        selected_item = self.text_tree.selection()
        if selected_item:
            item = self.text_tree.item(selected_item)
        raw_date = str(item['values'][0]).strip()
        formatted_date = raw_date        
        filepath = os.path.join(TEXT_FOLDER, f"{formatted_date}.txt")       
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                full_body = f.read()
        else:
            full_body = "本文ファイルが見つかりませんでした。"

        self.show_popup(raw_date, full_body)
    def show_popup(self, date, body):
        popup = tk.Toplevel()
        popup.title(f"{date} の日記全文")

        text = tk.Text(popup, wrap="word", width=60, height=20)
        text.insert("1.0", body)
        text.config(state="disabled")
        text.pack(padx=10, pady=10)
        
    def push_help(self):
        messagebox.showinfo('ヘルプ','これまでの記録が確認できます\nテキストの本文をダブルクリックすると詳細表示')
    
    def destroy(self):
        super().destroy()
    #    self.canvas.unbind("<MouseWheel>")
    #    self.canvas.unbind("<Configure>")
    #    self.scrollable_frame.unbind("<Configure>")
    #    self.text_tree.unbind("<Double-1>")
    #    self.scrollbar.config(command="")  # コールバック解除
    #    self.canvas.configure(yscrollcommand="")  # 同上