import tkinter as tk
from ui.interface import BlackjackInterface

if __name__ =="__main__":
    root = tk.Tk()
    app = BlackjackInterface(root)
    root.mainloop()