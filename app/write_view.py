import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from google.generativeai import configure, GenerativeModel
import csv
import os

class DiaryApp(tk.Frame):
    def __init__(self, master, dates, switch_frame_callback):
        super().__init__(master)
        self.master = master
        self.dates = dates
        self.switch_frame_callback = switch_frame_callback
        
        # --- GUIのセットアップ ---
        # root = tk.Tk()
        # root.title("Text Widget Character Limit")

        # text_widget = tk.Text(root, wrap="word", height=10, width=50)
        # text_widget.pack(padx=10, pady=10)
        
        
        self.weath = {'晴れ☀':0,'曇り☁':1,'雨☂':2,'雪':3}
        self.act = {'出社':0,'テレワーク':1,'外回り':2,'出張':3,'休日':4}
        self.weather_select = ['晴れ','曇り','雨','雪']
        self.act_select = ['出社','テレワーク','外回り','出張','休日']
        
        self.folder = 'data'
        self.filename = 'diary_data.csv'
        self.textfold = os.path.join('data','texts')
        self.textfile = f'{dates}.txt'
        self.filepath = os.path.join(self.folder, self.filename)
        self.txtpath = os.path.join(self.textfold, self.textfile)
        
        # ウィンドウの設定
        master.geometry('400x400')
        master.title('日記アプリ')
        
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

        self.api_key = os.getenv('API_Gemini')
        configure(api_key=self.api_key)
        self.model = GenerativeModel('models/gemini-2.0-flash')
    
    def resize_canvas(self, event):
        # キャンバスのサイズを親ウィンドウに合わせて調整
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def create_widgets(self):
        # ヘッダーフレーム（メニューバー）
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # メニューバー
        menubar = tk.Menu(self.master)
        self.master.configure(menu=menubar)
        diary_menu = tk.Menu(menubar, tearoff=0)
        
        menubar.add_cascade(label='日記メニュー', menu=diary_menu)
        
        diary_menu.add_command(label='日記作成', command=self.diary_write)
        diary_menu.add_command(label='日記一覧', command=self.diary_list)
        
        # メインコンテンツフレーム
        content_frame = ttk.Frame(self.scrollable_frame, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 充実度
        fulfillment_frame = ttk.Frame(content_frame)
        fulfillment_frame.pack(fill=tk.X, pady=6)
        
        fulfillment_label = ttk.Label(fulfillment_frame, text="充実度", font=('Helvetica', 12))
        fulfillment_label.pack(anchor='center', pady=(0, 10))

        slider_container = ttk.Frame(fulfillment_frame)
        slider_container.pack(fill=tk.X, pady=5)
        
        # 「低い」ラベル
        low_label = ttk.Label(slider_container, text="低", font=('Helvetica', 9))
        low_label.pack(side=tk.LEFT)

        # スライダー
        self.slider = ttk.Scale(slider_container, from_=0, to=100, orient=tk.HORIZONTAL, length=250)
        self.slider.set(50)
        self.slider.pack(side=tk.LEFT, expand=True,fill=tk.X, padx=(5, 5))

        # 「高い」ラベル
        high_label = ttk.Label(slider_container, text="高", font=('Helvetica', 9))
        high_label.pack(side=tk.LEFT)
        
        # ドロップダウンフレーム
        dropdowns_frame = ttk.Frame(content_frame)
        dropdowns_frame.pack(fill=tk.X, pady=20)
        
        # 天気ドロップダウン
        weather_frame = ttk.Frame(dropdowns_frame)
        weather_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        weather_list = ['晴れ☀', '雨☂', '曇り☁']
        self.weather_combo = ttk.Combobox(weather_frame, values=weather_list, state='readonly')
        self.weather_combo.set("天気")
        self.weather_combo.pack(fill=tk.X)
        
        # 行動ドロップダウン
        action_frame = ttk.Frame(dropdowns_frame)
        action_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        action_list = ["出社", "テレワーク", "外回り", "出張", "休日"]
        self.action_combo = ttk.Combobox(action_frame, values=action_list, state='readonly')
        self.action_combo.set("主な行動")
        self.action_combo.pack(fill=tk.X)
        
        # テキストエリア
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # テキストエリアとスクロールバー
        text_font = Font(family="Helvetica", size=10)
        self.text = tk.Text(text_frame, width=50, height=12, font=text_font, 
                           borderwidth=1, relief="solid", padx=8, pady=8)
        self.text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scrollbar.set)
# キーが離されたときに関数を呼び出すようにバインド
# <KeyRelease> はキー入力後に発生するイベント
        self.text.bind("<KeyRelease>", self.limit_text_length)
        
        # フッターフレーム（保存ボタン）
        footer_frame = ttk.Frame(self.scrollable_frame)
        footer_frame.pack(fill=tk.X)
        
        self.save_button = ttk.Button(footer_frame, text="保存", width=10, 
                                     command=self.save_diary)
        self.save_button.pack(side=tk.RIGHT, padx=40,pady=(0, 20))
        
        # マウスホイールでスクロールを可能にする
        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        # Windowsの場合
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def diary_write(self):
        self.slider.set(50)
        self.weather_combo.set("天気")
        self.action_combo.set("主な行動")
        self.text.delete(1.0, tk.END)
        messagebox.showinfo("新規作成", "新しい日記を作成します")
    
    def diary_list(self):
        pass
    
    
    
    def limit_text_length(self, event):
        """Textウィジェットの文字数を制限する関数"""
        widget = event.widget
    # 現在のテキスト内容を取得 (末尾の改行を除く)
        content = widget.get("1.0", "end-1c")
    # 文字数をチェック
        if len(content) > 200:
        # 200文字を超える部分を削除
        # "1.0 + 200 chars" は 1行目の0文字目から数えて200文字目以降を指定
            widget.delete("1.0 + 200 chars", "end")
        # 警告を出すなどの処理もここに追加可能
            selectbackground = "#ffcccc"  # 赤色 
            
    def save_diary(self):
        fulfillment = self.slider.get()
        weat_get = self.weather_combo.get()
        weather = self.weath[weat_get]
        act_get = self.action_combo.get()
        action = self.act[act_get]
        content = self.text.get(1.0, tk.END)

        prompt = f"今日の充実度は{fulfillment}、天気は{weat_get}、主な行動は{act_get}です。内容は以下の通りです。\n\n{content}"
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        
        with open(self.filepath, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([self.dates, weather, fulfillment, action])
            
        with open(self.txtpath, mode='a', newline='', encoding='utf-8') as file:
            file.write(f"{content}")
    
        messagebox.showinfo("保存完了", f"日記が保存されました。\n\nジェミニ先生からのコメント\n\n{response_text}")


if __name__ == '__main__':
    root = tk.Tk()
    app = DiaryApp(root)
    root.mainloop()