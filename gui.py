"""""
Scans given folder for games (aka .exe files), then adds them to a list which the user
can launch the games from. Stores the user's Steam login info and uses it to
automatically log in to Steam as needed.
"""""

from tkinter import *
from tkinter import filedialog
import sqlite3 as sql
from helper import search

conn = sql.connect('launch.db')
db = conn.cursor()

root = Tk()
root.title("Ivy's Game Launcher")
root.geometry("800x600")



# !!!FUNCTIONS!!!
""" Get folder location"""
def folderPath(entry):
    path = filedialog.askdirectory()
    entry.delete(0, END)
    entry.insert(0, path)

def scanWindow():
    scan = Toplevel(root)
    scan.title("Scan Folder")
    scan.geometry("400x600")
    scan.grab_set()
    # !!!ENTRIES!!!
    pathEntry = Entry(scan, width=50)
    pathEntry.grid(column=1, row=0)

    # !!!BUTTONS!!!
    pathButton = Button(scan, text="Folder", command=lambda: folderPath(pathEntry))
    pathButton.grid(column=0, row=0)
    pathString = pathEntry.get()

    scanButton = Button(scan, text="Find Games!", command=lambda: search(pathString))
    scanButton.grid(column=1, row=1)

# !!!MENUS!!!
menuBar = Menu(root)
menuBar.add_command(label="Scan", command=scanWindow)
# Add menu to root window
root.config(menu=menuBar)


root.mainloop()
conn.close()
