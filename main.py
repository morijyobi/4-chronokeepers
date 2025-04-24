import tkinter as tk
# from app.calendar_view import CalendarView

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("日記アプリ")
        self.geometry("600x400")

        # 最初の画面を表示
        # self.frame = CalendarView(self)
        self.frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()