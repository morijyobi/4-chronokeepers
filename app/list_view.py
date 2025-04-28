import tkinter as tk

class ListView(tk.Frame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.switch_frame_callback = switch_frame_callback
        self.pack()
        
        master.geometry('400x400')
        master.title('日記一覧画面')
        
        self.create_widgets()
        
        
    def create_widgets(self):
        pass