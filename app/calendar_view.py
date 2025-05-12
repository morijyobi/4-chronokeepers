import tkinter as tk
from PIL import Image, ImageTk
from tkcalendar import Calendar
from tkinter import messagebox

class CalendarView(tk.Frame):
    def __init__(self, master, switch_frame_callback, test_mode=False):
        super().__init__(master)
        self.switch_frame_callback = switch_frame_callback
        self.test_mode = test_mode
        self.pack(fill='both', expand=True)

        master.geometry('600x500')
        master.title('メイン画面')

        self.create_widgets()

    def create_widgets(self):
        menubar = tk.Menu(self.master)
        self.master.configure(menu=menubar)
        diary_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='日記メニュー', menu=diary_menu)
        diary_menu.add_command(label='日記作成', command=lambda: self.switch_frame_callback("calendar"))
        diary_menu.add_command(label='日記一覧', command=lambda: self.switch_frame_callback("list"))
        menubar.add_command(label='ヘルプ', command=self.push_help)

        if not self.test_mode:
            penimg = Image.open("img/pen.png")  # 実際の画像読み込み
            pen_width = 50
            pen_height = 50
            resized_pen = penimg.resize((pen_width, pen_height))
            self.pen_icon_resized = ImageTk.PhotoImage(resized_pen)
        else:
            self.pen_icon_resized = None  # テスト時は画像を使わない

        self.label = tk.Label(self, text="日付を選んでボタンを押してください")
        self.label.place(relx=0.3, y=10)
        self.cal = Calendar(self, selectmode='day', date_pattern='yyyy-mm-dd',
                            showweeknumbers=False, firstweekday='monday', font="Arial 13")
        self.cal.place(x=55, y=50)
        self.pen_button = tk.Button(self, image=self.pen_icon_resized, command=self.show_selected_date)
        self.pen_button.place(x=170, y=270)

    def show_selected_date(self):
        selected_date = self.cal.get_date()
        self.switch_frame_callback("write", selected_date)
        
    def push_help(self):
        messagebox.showinfo('ヘルプ','カレンダーの日付を選択して、カレンダーの下のボタンを押す')