import tkinter as tk
from PIL import Image, ImageTk
from tkcalendar import Calendar
from write_view import DiaryApp
from list_view import Application

class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        
        master.geometry('400x400')
        master.title('メイン画面')
        
        self.create_widgets()
        
    def create_widgets(self):
        menubar = tk.Menu(self.master)
        self.master.configure(menu=menubar)
        diary_menu = tk.Menu(menubar,tearoff=0)
        menubar.add_cascade(label='日記メニュー',menu=diary_menu)
        diary_menu.add_command(label='日記作成',command=self.diary_write)
        diary_menu.add_command(label='日記一覧',command=self.diary_list)
        
        penimg = Image.open("img\鉛筆の無料アイコン7 .png") # リサイズしたいアイコンのファイル名
        pen_width = 50  # 希望の幅 (ピクセル)
        pen_height = 50 # 希望の高さ (ピクセル)
        resized_pen = penimg.resize((pen_width, pen_height))
        self.pen_icon_resized = ImageTk.PhotoImage(resized_pen)
        
        self.label = tk.Label(self, text="日付を選んでボタンを押してください")
        self.label.place(relx=0.3, y=10)
        self.cal = Calendar(self, selectmode='day', date_pattern='yyyy-mm-dd', showweeknumbers=False, firstweekday='monday', font = "Arial 13")
        self.cal.place(x=55, y=50)
        self.pen_button = tk.Button(self, image=self.pen_icon_resized, command=self.show_selected_date)
        self.pen_button.place(x=170, y=270)

    def show_selected_date(self):
        selected_date = self.cal.get_date()
        print(f'選択された日付: {selected_date}')
        self.destroy()
        DiaryApp(self.master)
        
    def diary_write(self):
        self.destroy()
        DiaryApp(self.master)

    def diary_list(self):
        self.destroy()
        Application(self.master)

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()