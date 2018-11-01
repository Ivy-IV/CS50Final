"""""
Scans given folder for games (aka .exe files), then adds them to a list which the user
can launch the games from. Stores the user's Steam login info and uses it to
automatically log in to Steam as needed.
"""""

from tkinter import *
from tkinter import filedialog
from sqlite3 import *
from helper import search
from pathlib import Path

conn = connect('launcher.db')
db = conn.cursor()

root = Tk()
root.title("Ivy's Game Launcher")
root.geometry("800x600")



# !!!FUNCTIONS!!!
""" Get folder location"""

def scanWindow():
    scan = Toplevel(root)
    scan.title("Scan Folder")
    scan.geometry("400x600")
    scan.grid_columnconfigure(index=1, weight=1)
    scan.grab_set()

    def getList(type):
        # Add single file to list
        if type == 0:
            path = filedialog.askopenfilename()
            if Path(path) not in [Path(i) for i in addList.get(0, END)]: addList.insert(END, path)
        # Scan folder and add contents to list
        elif type == 1:
            path = filedialog.askdirectory()
            games = search(path)
            for item in games:
                if Path(item) not in [Path(i) for i in addList.get(0, END)]: addList.insert(END, item)
        addButton.grid(column=5, row=5, sticky=SE)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!TODO!!!!!!!!!!!!!
    def addGame():
        select = addList.curselection()
        for i in select:
            path = addList.get(i)
            print(path)
            rows = db.execute("SELECT path FROM noDRM WHERE path=?", (path,))
            print(rows.fetchall())
            # Returns generator object --- need to use result in condition
            if rows.fetchall() == []:
                rows = db.execute("INSERT INTO noDRM('name', 'path') VALUES(?, ?)",
                    (Path(path).stem, path,))
                print(rows.fetchall())
        conn.commit()

    # !!!LIST!!!
    scrolly = Scrollbar(scan)
    scrolly.grid(column=3, rowspan=2, sticky=NS)
    scrollx = Scrollbar(scan, orient=HORIZONTAL)
    scrollx.grid(column=1, columnspan=2, row=2, sticky=EW)
    addList = Listbox(scan, selectmode=MULTIPLE,
    yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
    addList.grid(column=1, columnspan=2, row=0, rowspan = 2, sticky=EW+NS,)
    scrolly.config(command=addList.yview)
    scrollx.config(command=addList.xview)
    # !!!BUTTONS!!!
    fileButton = Button(scan, text="Select File", command=lambda: getList(0))
    fileButton.grid(column=0, row=0, sticky=N+EW)

    folderButton = Button(scan, text="Scan Folder", command=lambda: getList(1))
    folderButton.grid(column=0, row=1, sticky=N+EW)

    addButton = Button(scan, text="Add to Games", command=addGame)




# !!!MENUS!!!
menuBar = Menu(root)
menuBar.add_command(label="Scan", command=scanWindow)
# Add menu to root window
root.config(menu=menuBar)


root.mainloop()
conn.close()
