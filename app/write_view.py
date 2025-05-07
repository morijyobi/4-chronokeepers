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
        # master.geometry('400x400') # 重複しているので一方をコメントアウトまたは削除

        # 自分自身を配置
        self.pack(fill='both', expand=True)

        # スクロール可能なキャンバスを作成（self に対して）
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
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
        if not self.api_key:
            messagebox.showerror("エラー", "APIキーが設定されていません。\n環境変数 'API_Gemini' を設定してください。")
            self.master.destroy() # APIキーがない場合はアプリケーションを終了
            return
        configure(api_key=self.api_key)

        self.model = GenerativeModel('gemini-1.5-flash')
    
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

        scrollbar_text = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview) # 変数名を変更
        scrollbar_text.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scrollbar_text.set)

        # ボタンフレーム

        footer_frame = ttk.Frame(self.scrollable_frame)
        footer_frame.pack(fill=tk.X, pady=(10,0)) # 上に少しマージンを追加


        # フッター内のボタン用内部フレーム (右寄せのため)
        buttons_inner_frame = ttk.Frame(footer_frame)
        buttons_inner_frame.pack(side=tk.RIGHT, padx=(0,15),pady=(0, 20))


        self.teach_button = ttk.Button(buttons_inner_frame, text="添削", width=10, # 変数名を変更

                                     command=self.teach_diary)
        self.teach_button.pack(side=tk.LEFT, padx=(0,5)) # 左から配置、右にマージン
        
        self.save_button = ttk.Button(buttons_inner_frame, text="保存", width=10, 
                                     command=self.save_diary)
        self.save_button.pack(side=tk.LEFT) # 左から配置
        
        # マウスホイールでスクロールを可能にする

        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel, add="+") # add="+" を追加

    def _on_mousewheel(self, event):
        # Linuxの場合、event.deltaの値が異なることがあるため調整
        if os.name == 'posix': # Linuxの場合
            if event.num == 4: # 上スクロール
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5: # 下スクロール
                self.canvas.yview_scroll(1, "units")
        else: # WindowsやMacの場合
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


    def diary_write(self):
        self.slider.set(50)
        self.weather_combo.set("天気")
        self.action_combo.set("主な行動")
        self.text.delete(1.0, tk.END)
        messagebox.showinfo("新規作成", "新しい日記を作成します")


    def _show_loading_screen(self):
        """ロード中画面を表示する"""
        self.loading_window = tk.Toplevel(self.master)
        self.loading_window.title("処理中")
        self.loading_window.geometry("200x100")
        # 親ウィンドウの中央に表示
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (200 // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (100 // 2)
        self.loading_window.geometry(f"+{x}+{y}")

        self.loading_window.transient(self.master) # 親ウィンドウの上に表示
        self.loading_window.grab_set() # モーダルにする
        loading_label = ttk.Label(self.loading_window, text="ロード中...", font=('Helvetica', 12))
        loading_label.pack(expand=True)
        self.loading_window.resizable(False, False) # サイズ変更不可
        self.master.update_idletasks() # UIの更新を強制

    def _hide_loading_screen(self):
        """ロード中画面を非表示にする"""
        if hasattr(self, 'loading_window') and self.loading_window.winfo_exists():
            self.loading_window.destroy()
            del self.loading_window # 属性を削除

    def _perform_save(self, fulfillment, weather, action, content):
        """実際の保存処理とAI呼び出し"""
        try:
            prompt = f""" 
            今日の充実度は{fulfillment}、天気は{weather}、主な行動は{action}です。内容は以下の通りです。\n\n{content}"""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
        with open(self.filepath, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([self.dates, weather, fulfillment, action])
            
        with open(self.txtpath, mode='a', newline='', encoding='utf-8') as file:
            file.write(f"{content}")
            # メインスレッドでUI更新をスケジュール
            self.master.after(0, self._show_save_result, response_text)
        except Exception as e:
            # メインスレッドでエラー表示をスケジュール
            self.master.after(0, self._show_error, f"保存処理中にエラーが発生しました:\n{e}")
        finally:
            # メインスレッドでロード画面非表示をスケジュール
            self.master.after(0, self._hide_loading_screen)

    def _show_save_result(self, response_text):
        """保存結果をメッセージボックスで表示"""
        messagebox.showinfo("保存完了", f"日記が保存されました。\n\nジェミニ先生からのコメント\n\n{response_text}")

    def save_diary(self):
        fulfillment = int(self.slider.get())
        weather = self.weather_combo.get()
        action = self.action_combo.get()
        content = self.text.get(1.0, tk.END).strip() # 末尾の改行を削除

        if not content:
            messagebox.showwarning("入力エラー", "日記の内容を入力してください。")
            return
        if weather == "天気":
            messagebox.showwarning("入力エラー", "天気を選択してください。")
            return
        if action == "主な行動":
            messagebox.showwarning("入力エラー", "主な行動を選択してください。")
            return

        self._show_loading_screen()
        # 別スレッドで保存処理を実行
        thread = threading.Thread(target=self._perform_save, args=(fulfillment, weather, action, content))
        thread.start()

    def _perform_teach(self, fulfillment, weather, action, content):
        """実際の添削処理とAI呼び出し"""
        try:
            prompt = f"""※これは日記です。内容について改善点を教えていただけますか。なお会話は続けるプログラムは組まれていません。
            今日の充実度は{fulfillment}、天気は{weather}、主な行動は{action}です。内容は以下の通りです。\n\n{content}"""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            # メインスレッドでUI更新をスケジュール
            self.master.after(0, self._show_teach_result, response_text)
        except Exception as e:
            # メインスレッドでエラー表示をスケジュール
            self.master.after(0, self._show_error, f"添削処理中にエラーが発生しました:\n{e}")
        finally:
            # メインスレッドでロード画面非表示をスケジュール
            self.master.after(0, self._hide_loading_screen)

    def _show_teach_result(self, response_text):
        """添削結果をメッセージボックスで表示"""
        messagebox.showinfo("添削完了", f"添削されました。\n\nジェミニ先生からのアドバイス\n\n{response_text}")
    
    def _show_error(self, error_message):
        """エラーメッセージを表示"""
        messagebox.showerror("エラー", error_message)
    
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
            

    def teach_diary(self):
        fulfillment = int(self.slider.get())
        weather = self.weather_combo.get()
        action = self.action_combo.get()
        content = self.text.get(1.0, tk.END).strip() # 末尾の改行を削除

        if not content:
            messagebox.showwarning("入力エラー", "日記の内容を入力してください。")
            return
        if weather == "天気":
            messagebox.showwarning("入力エラー", "天気を選択してください。")
            return
        if action == "主な行動":
            messagebox.showwarning("入力エラー", "主な行動を選択してください。")
            return

        self._show_loading_screen()
        # 別スレッドで添削処理を実行
        thread = threading.Thread(target=self._perform_teach, args=(fulfillment, weather, action, content))
        thread.start()
        
    def destroy(self):
        # バインドを解除
        self.scrollable_frame.unbind_all("<MouseWheel>") # ここで解除
        super().destroy()

# --- アプリケーション実行のためのサンプルコード (通常は別ファイル) ---
if __name__ == '__main__':
    # 環境変数 API_Gemini にご自身のAPIキーを設定してください
    # 例: os.environ['API_Gemini'] = "YOUR_API_KEY"
    
    # ダミーのコールバック関数とdates
    def switch_frame(frame_name):
        print(f"Switching to {frame_name}")

    dummy_dates = {"2024-01-01": "元旦の日記"}

    root = tk.Tk()
    app = DiaryApp(root, dummy_dates, switch_frame)
    root.mainloop()