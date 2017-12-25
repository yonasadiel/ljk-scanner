import tkinter as tk
from tkinter import filedialog
import ljk_scanner

root = tk.Tk()
foldername = filedialog.askdirectory()
root.destroy()
print(foldername)
ljk_scanner.main(foldername)
