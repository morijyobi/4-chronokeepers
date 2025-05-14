import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from google.generativeai import configure, GenerativeModel
import csv
import os
import threading # スレッド処理のために追加

class DiaryApp(tk.Frame):
    def __init__(self, master, dates, switch_frame_callback):
        super().__init__(master)
        self.master = master
        self.dates = str(dates) # datesが確実に文字列になるようにする
        self.switch_frame_callback = switch_frame_callback
        self.api_key = None
        self.model = None
        # self.setup_model()  # ★★★ この呼び出しを削除 ★★★

        # --- GUIのセットアップのための他の属性初期化 ---
        self.weath = {'晴れ☀':0,'曇り☁':1,'雨☂':2,'雪☃':3}
        self.act = {'出社':0,'テレワーク':1,'外回り':2,'出張':3,'休日':4}
        self.weather_select_csv = ['晴れ','曇り','雨','雪']
        self.act_select_csv = ['出社','テレワーク','外回り','出張','休日']
        
        self.folder = 'data'
        self.filename = 'diary_data.csv'
        self.textfold = os.path.join(self.folder,'texts') # 'data/texts'
        
        if not os.path.exists(self.textfold):
            os.makedirs(self.textfold)
            
        self.textfile = f'{self.dates}.txt' # self.dates を使用
        self.filepath = os.path.join(self.folder, self.filename) # data/diary_data.csv
        self.txtpath = os.path.join(self.textfold, self.textfile) # data/texts/YYYY-MM-DD.txt
        
        # ウィンドウの設定 (API初期化成功後に移動)
        # master.geometry('600x500')
        # master.title('日記アプリ')
        # self.pack(fill='both', expand=True)

        self.create_widgets() # GUIウィジェットを作成

        # ★★★ APIモデルの初期化をここに移動し、setup_modelを呼び出す ★★★
        if not self.setup_model(): # API初期化を実行
            # setup_model内でエラー表示とウィンドウ破棄が行われる可能性がある
            if not (hasattr(self.master, 'winfo_exists') and self.master.winfo_exists()):
                return # __init__ の処理を中断

        # API初期化が成功した後にウィンドウの最終設定と表示を行う
        master.geometry('600x500')
        master.title('日記アプリ')
        self.pack(fill='both', expand=True) # DiaryAppフレーム自身を配置

        # ★★★ 以前ここにあったAPIキー設定とモデル初期化のブロックは setup_model に統合されたため削除 ★★★
        # self.api_key = os.getenv('API_Gemini')
        # if not self.api_key:
        #     messagebox.showerror("エラー", "APIキーが設定されていません。\n環境変数 'API_Gemini' を設定してください。")
        #     self.master.destroy()
        #     return
        # try:
        #     configure(api_key=self.api_key)
        #     self.model = GenerativeModel('gemini-1.5-flash')
        # except Exception as e:
        #     messagebox.showerror("API設定エラー", f"Geminiモデルの初期化に失敗しました: {e}")
        #     self.master.destroy()
        #     return
    
    def create_widgets(self):
        # ヘッダーフレーム（メニューバー用コンテナだが、メニューはmasterに配置）
        # header_frame = ttk.Frame(self) # メニューはmasterに直接設定するので、このフレームは実質不要かも
        # header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # メニューバー
        menubar = tk.Menu(self.master)
        self.master.configure(menu=menubar)
        diary_menu = tk.Menu(menubar, tearoff=0)
        
        menubar.add_cascade(label='日記メニュー', menu=diary_menu)
        
        diary_menu.add_command(label='日記作成', command=lambda: self.switch_frame_callback("calendar"))
        diary_menu.add_command(label='日記一覧', command=lambda: self.switch_frame_callback("list"))
        menubar.add_command(label='ヘルプ', command=self.push_help)
        
        # メインコンテンツフレーム (self に直接配置)
        content_frame = ttk.Frame(self, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 充実度
        fulfillment_frame = ttk.Frame(content_frame)
        fulfillment_frame.pack(fill=tk.X, pady=6)
        
        fulfillment_label = ttk.Label(fulfillment_frame, text="充実度", font=('Helvetica', 12))
        fulfillment_label.pack(anchor='center', pady=(0, 10))

        slider_container = ttk.Frame(fulfillment_frame)
        slider_container.pack(fill=tk.X, pady=5)
        
        low_label = ttk.Label(slider_container, text="低", font=('Helvetica', 9))
        low_label.pack(side=tk.LEFT)

        self.slider = ttk.Scale(slider_container, from_=0, to=100, orient=tk.HORIZONTAL, length=250)
        self.slider.set(50)
        self.slider.pack(side=tk.LEFT, expand=True,fill=tk.X, padx=(5, 5))

        high_label = ttk.Label(slider_container, text="高", font=('Helvetica', 9))
        high_label.pack(side=tk.LEFT)
        
        # ドロップダウンフレーム
        dropdowns_frame = ttk.Frame(content_frame)
        dropdowns_frame.pack(fill=tk.X, pady=20)
        
        weather_frame = ttk.Frame(dropdowns_frame)
        weather_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        weather_list = ['晴れ☀', '雨☂', '曇り☁', '雪☃'] # 雪を追加
        self.weather_combo = ttk.Combobox(weather_frame, values=weather_list, state='readonly')
        self.weather_combo.set("天気")
        self.weather_combo.pack(fill=tk.X)
        
        action_frame = ttk.Frame(dropdowns_frame)
        action_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        action_list = ["出社", "テレワーク", "外回り", "出張", "休日"]
        self.action_combo = ttk.Combobox(action_frame, values=action_list, state='readonly')
        self.action_combo.set("主な行動")
        self.action_combo.pack(fill=tk.X)
        
        # テキストエリア
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        text_font = Font(family="Helvetica", size=10)
        self.text = tk.Text(text_frame, width=50, height=12, font=text_font, 
                           borderwidth=1, relief="solid", padx=8, pady=8, wrap="word")
        self.text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar_text = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        scrollbar_text.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scrollbar_text.set)
        self.text.bind("<KeyRelease>", self.limit_text_length)
        
        # フッターフレーム（ボタン用） (self に直接配置)
        footer_frame = ttk.Frame(self)
        footer_frame.pack(fill=tk.X, pady=(10,0))

        buttons_inner_frame = ttk.Frame(footer_frame)
        buttons_inner_frame.pack(side=tk.RIGHT, padx=(0,15) ,pady=(0,20))


        self.teach_button = ttk.Button(buttons_inner_frame, text="添削", width=10,
                                     command=self.teach_diary)
        self.teach_button.pack(side=tk.LEFT, padx=(0,5))
        
        self.save_button = ttk.Button(buttons_inner_frame, text="保存", width=10, 
                                     command=self.save_diary)
        self.save_button.pack(side=tk.LEFT)
    
    def diary_write(self):
        self.slider.set(50)
        self.weather_combo.set("天気")
        self.action_combo.set("主な行動")
        self.text.delete(1.0, tk.END)
        messagebox.showinfo("新規作成", "新しい日記を作成します")
    
    def limit_text_length(self, event):
        widget = event.widget
        content = widget.get("1.0", "end-1c")
        if len(content) > 200:
            widget.delete("1.0 + 200 chars", "end")

    def _show_loading_screen(self):
        self.loading_window = tk.Toplevel(self.master)
        self.loading_window.title("処理中")
        self.loading_window.geometry("200x100")
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (200 // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (100 // 2)
        self.loading_window.geometry(f"+{x}+{y}")
        self.loading_window.transient(self.master)
        self.loading_window.grab_set()
        loading_label = ttk.Label(self.loading_window, text="ロード中...", font=('Helvetica', 12))
        loading_label.pack(expand=True)
        self.loading_window.resizable(False, False)
        self.master.update_idletasks()

    def _hide_loading_screen(self):
        if hasattr(self, 'loading_window') and self.loading_window.winfo_exists():
            self.loading_window.grab_release()
            self.loading_window.destroy()
            del self.loading_window

    def _show_error(self, error_message):
        self._hide_loading_screen() 
        messagebox.showerror("エラー", error_message, parent=self.master)

    def _perform_save(self, fulfillment_val, weather_key, action_key, content_text, weather_val_csv, action_val_csv):
        try:
            if not self.model:
                self.master.after(0, self._show_error, "APIモデルが初期化されていません。")
                return

            prompt = f"今日の充実度は{fulfillment_val}、天気は{weather_key}、主な行動は{action_key}です。内容は以下の通りです。\n\n{content_text}"
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            file_exists = os.path.isfile(self.filepath)
            with open(self.filepath, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists or os.path.getsize(self.filepath) == 0: 
                    writer.writerow(['date', 'weather', 'fulfillment', 'action']) 
                writer.writerow([self.dates, weather_val_csv, fulfillment_val, action_val_csv])
                
            with open(self.txtpath, mode='w', encoding='utf-8') as file: 
                file.write(content_text)
    
            self.master.after(0, self._show_save_result, response_text)
        except Exception as e:
            self.master.after(0, self._show_error, f"保存処理中にエラーが発生しました:\n{e}")
        finally:
            self.master.after(0, self._hide_loading_screen)


    def _show_save_result(self, response_text):
        self._hide_loading_screen() 
        messagebox.showinfo("保存完了", f"日記が保存されました。\n\nジェミニ先生からのコメント\n\n{response_text}", parent=self.master)
        self.switch_frame_callback("calendar")

    def save_diary(self):
        fulfillment = int(self.slider.get()) 
        weat_get = self.weather_combo.get()
        act_get = self.action_combo.get()
        content = self.text.get(1.0, tk.END).strip()

        if weat_get == "天気":
            messagebox.showwarning("入力エラー", "天気を選択してください。", parent=self.master)
            return
        if act_get == "主な行動":
            messagebox.showwarning("入力エラー", "主な行動を選択してください。", parent=self.master)
            return
        if not content:
            messagebox.showwarning("入力エラー", "日記の内容を入力してください。", parent=self.master)
            return
        
        try:
            weather_csv_val = self.weath[weat_get] 
            action_csv_val = self.act[act_get]   
        except KeyError as e:
            messagebox.showerror("内部エラー", f"選択された値の変換に失敗しました: {e}", parent=self.master)
            return
         
        self._show_loading_screen()
        thread = threading.Thread(target=self._perform_save, args=(fulfillment, weat_get, act_get, content, weather_csv_val, action_csv_val))
        thread.start()

    def _perform_teach(self, fulfillment_val, weather_key, action_key, content_text):
        try:
            if not self.model:
                self.master.after(0, self._show_error, "APIモデルが初期化されていません。")
                return

            prompt = f"""※これは日記です。内容について改善点を教えていただけますか。なお会話は続けるプログラムは組まれていません。
            今日の充実度は{fulfillment_val}、天気は{weather_key}、主な行動は{action_key}です。内容は以下の通りです。\n\n{content_text}"""
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            self.master.after(0, lambda: messagebox.showinfo(
                "添削完了", f"ジェミニ先生からのアドバイス\n\n{response_text}", parent=self.master # タイトルを修正
            ))
        except Exception as e:
            self.master.after(0, self._show_error, f"添削処理中にエラーが発生しました:\n{e}")
        finally:
            self.master.after(0, self._hide_loading_screen)

    def _show_teach_result(self, response_text): # このメソッドは現在直接呼ばれていないが、念のため残す
        self._hide_loading_screen()
        messagebox.showinfo("添削完了", f"添削されました。\n\nジェミニ先生からのアドバイス\n\n{response_text}", parent=self.master)

    def teach_diary(self):
        fulfillment = int(self.slider.get())
        weather = self.weather_combo.get()
        action = self.action_combo.get()
        content = self.text.get(1.0, tk.END).strip()

        if weather == "天気":
            messagebox.showwarning("入力エラー", "天気を選択してください。", parent=self.master)
            return
        if action == "主な行動":
            messagebox.showwarning("入力エラー", "主な行動を選択してください。", parent=self.master)
            return
        if not content:
            messagebox.showwarning("入力エラー", "日記の内容を入力してください。", parent=self.master)
            return

        # ★★★ 不要な messagebox.showinfo を削除 ★★★
        # messagebox.showinfo("添削", f"添削されました。\n\nジェミニ先生からのアドバイス\n\n{response_text}")
        
        self._show_loading_screen()
        thread = threading.Thread(target=self._perform_teach, args=(fulfillment, weather, action, content))
        thread.start()

    # ★★★ setup_model メソッドを修正 ★★★
    def setup_model(self):
        """ Gemini API の初期化を行うメソッド """
        # GUI要素へのアクセスやスレッド開始処理を削除
        # fulfillment = int(self.slider.get())
        # weather = self.weather_combo.get()
        # action = self.action_combo.get()
        # content = self.text.get(1.0, tk.END).strip()
        
        if self.model: # 既に初期化済みであれば何もしない
            return True

        self.api_key = os.getenv('API_Gemini')
        if not self.api_key:
            messagebox.showerror("エラー", "APIキーが設定されていません。\n環境変数 'API_Gemini' を設定してください。", parent=self.master)
            if hasattr(self.master, 'destroy') and self.master.winfo_exists(): # masterが破棄可能か確認
                self.master.destroy()
            return False # APIキーがない場合は失敗

        try:
            configure(api_key=self.api_key)
            # モデル名を 'gemini-1.5-flash' に統一 (以前のコードで使われていたため)
            self.model = GenerativeModel('gemini-1.5-flash') 
            return True # 初期化成功
        except Exception as e:
            messagebox.showerror("API設定エラー", f"Geminiモデルの初期化に失敗しました: {e}", parent=self.master)
            if hasattr(self.master, 'destroy') and self.master.winfo_exists(): # masterが破棄可能か確認
                self.master.destroy()
            return False # 初期化失敗

        # スレッド開始処理を削除
        # self._show_loading_screen()
        # thread = threading.Thread(target=self._perform_teach, args=(fulfillment, weather, action, content))
        # thread.start()

    def push_help(self):
        messagebox.showinfo('ヘルプ','バーをスライドさせて充実度を決める\n天気と主な行動を選ぶ\n本文を入力', parent=self.master)
      
    def destroy(self):
        super().destroy()