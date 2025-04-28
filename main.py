import tkinter as tk
from app.calendar_view import CalendarView
from app.write_view import DiaryApp
from app.list_view import ListView

class Main(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("日記アプリ")

        self.current_frame = None
        self.switch_frame("calendar")

    def switch_frame(self, name, date=None):
        if self.current_frame:
            self.current_frame.destroy()

        if name == "calendar":
            self.current_frame = CalendarView(self, self.switch_frame)
        elif name == "write":
            self.current_frame = DiaryApp(self, date, self.switch_frame)
        elif name == "list":
            self.current_frame = ListView(self, self.switch_frame)

        self.current_frame.pack()

if __name__ == "__main__":
    app = Main()
    app.mainloop()