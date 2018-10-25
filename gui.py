"""""
Scans given folder for games (aka .exe files), then adds them to a list which the user
can launch the games from. Stores the user's Steam login info and uses it to
automatically log in to Steam as needed.
"""""

from tkinter import *
from tkinter import filedialog
import sqlite3 as sql
from helper import search
from pathlib import Path

conn = sql.connect('launcher.db')
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

    def getList(path):
        games = search(path)
        print(games)
        addList = Listbox(scan, selectmode=MULTIPLE)
        addList.grid(column=0, row=2)
        for item in games:
            print(item)
            i = item.parent + "/" + item.stem
            print(i)
            addList.insert(END, i)

    # !!!BUTTONS!!!
    pathButton = Button(scan, text="Folder", command=lambda: folderPath(pathEntry))
    pathButton.grid(column=0, row=0)

    scanButton = Button(scan, text="Find Games!", command=lambda: getList(pathEntry.get()))
    scanButton.grid(column=1, row=1)



# !!!MENUS!!!
menuBar = Menu(root)
menuBar.add_command(label="Scan", command=scanWindow)
# Add menu to root window
root.config(menu=menuBar)


root.mainloop()
conn.close()
