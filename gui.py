"""""
Scans given folder for games (aka .exe files), then adds them to a list which the user
can launch the games from. Stores the user's Steam login info and uses it to
automatically log in to Steam as needed.
"""""

from tkinter import *
from tkinter import filedialog
from sqlite3 import *
from helper import *
from pathlib import Path
from subprocess import Popen, check_output, run

steamLog = False;

conn = connect('launcher.db')
db = conn.cursor()

root = Tk()
root.title("IVyVI Game Launcher")
root.geometry("800x600")
root.grid_columnconfigure(index=0, weight=1)
root.grid_rowconfigure(index=0, weight=1)

# !!!GAME LIST!!!
gScrolly = Scrollbar(root)
gScrolly.grid(column=3, rowspan=3, sticky=NS)
gScrollx = Scrollbar(root, orient=HORIZONTAL)
gScrollx.grid(columnspan=3, row=3, sticky=EW)
gameList = Listbox(root, selectmode=SINGLE,
yscrollcommand=gScrolly.set, xscrollcommand=gScrollx.set)
gameList.grid(columnspan=3, row=0, rowspan=3, sticky=EW+NS,)
gScrolly.config(command=gameList.yview)
gScrollx.config(command=gameList.xview)

# !!!FUNCTIONS!!!
def update():
    gameList.delete(0, END)
    rows = db.execute("SELECT name, path, drm FROM games ORDER BY drm, name")
    for i in rows:
        if i[2] == "No DRM": game = i[0], i[1]
        elif i[2] == "Steam": game = i[0], i[2]
        gameList.insert(END, game)

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
        return True

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!TODO!!!!!!!!!!!!!
    def addNoDRM():
        select = addList.curselection()
        for i in select:
            path = addList.get(i)
            noDInfo = [Path(path).stem, path, "No DRM",]
            rows = db.execute("SELECT path FROM games WHERE path=?", (path,))
            # Returns generator object --- need to use result in condition
            if path not in rows.fetchall():
                rows = db.execute("INSERT OR REPLACE INTO games('name', 'path', drm) VALUES(?, ?, ?)",
                    noDInfo)
        conn.commit()
        update()
        return True

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

    addButton = Button(scan, text="Add to Games", command=addNoDRM)

def steamWindow():
    steam = Toplevel(root)
    steam.title("Add Steam Games")
    steam.geometry("300x300")
    steam.grid_columnconfigure(index=1, weight=1)
    steam.grid_rowconfigure(index=9, weight=1)
    steam.grab_set()

    def steamDir(command):
        if command == "add":
            path = filedialog.askdirectory()
            if path not in [i for i in steamDirList.get(0, END)]:
                steamDirList.insert(END, path)
                return True
            else: return False
        elif command == "remove":
            select = steamDirList.curselection()
            for i in select:
                steamDirList.delete(i)
            return True

    def steamAdd():
        sList = steamSearch(steamDirList.get(0,END))
        for i in sList:
            rows = db.execute("SELECT steamid FROM games WHERE steamid=?", (i[0],))
            if i[0] not in rows.fetchall():
                ins = db.execute("INSERT OR REPLACE INTO games(steamid, name, drm) VALUES(?, ?, ?)", i)
        return True


    def steamQuit(command):
        if command == "ok":
            conn.commit()
            update()
        elif command == "cancel":
            conn.rollback()
        steam.destroy()

    #!!!!!LIST!!!!!
    steamScry = Scrollbar(steam)
    steamScry.grid(column=3, row=2, sticky=NS)
    steamScrx = Scrollbar(steam, orient=HORIZONTAL)
    steamScrx.grid(column=1, columnspan=2, row=3, sticky=EW)
    steamDirList = Listbox(steam, selectmode=MULTIPLE, height=5,
    yscrollcommand=steamScry.set, xscrollcommand=steamScrx.set)
    steamDirList.grid(column=1, columnspan=2, row=2, sticky=EW+NS,)
    steamScry.config(command=steamDirList.yview)
    steamScrx.config(command=steamDirList.xview)

    labelUser = Label(steam, text="Username").grid(column=0, row=0)
    enterUser = Entry(steam).grid(column=1, row=0, sticky=EW)
    labelPass = Label(steam, text="Password").grid(column=0, row=1)
    enterPass = Entry(steam, show='*').grid(column=1, row=1, sticky=N+EW)
    dirAddButton = Button(steam, text="Add Steam Directory", command=lambda:steamDir("add"))
    dirAddButton.grid(row=2, sticky=NE)
    dirRemButton = Button(steam, text="Remove Steam Directory", command=lambda:steamDir("remove"))
    dirRemButton.grid(row=2)
    steamButton = Button(steam, text="Update Steam List", command=steamAdd)
    steamButton.grid(column=1, row=4)
    okButton = Button(steam, text="OK", width=10, command=lambda: steamQuit("ok"))
    okButton.grid(column=1, row=10, sticky=SE)
    cancelButton = Button(steam, text="Cancel", width=10, command=lambda: steamQuit("cancel"))
    cancelButton.grid(column=0, row=10, sticky=SE)


def runGame():
    index = gameList.curselection()
    runName = gameList.get(index)[0]
    rows = db.execute("SELECT drm, path, steamid FROM games WHERE path=?", (runName,))
    gameInfo = rows.fetchone()
    if gameInfo[0] == "(Steam,)":
        # Check if Steam is running - found via:
        # https://stackoverflow.com/questions/25545937/check-if-process-is-running-in-windows-using-only-python-built-in-modules
        if steamLog == False:
            steamCheck = check_output('tasklist', shell=True)
            # TO FINISH
            if steamCheck == False:
                try: run(steamPath, "-login", steamUser, steamPass)
                except:
                    print("Login failed! oopsy")
                    return False
        try: run(steamPath, "-applaunch", gameInfo[2])
        except:
            print("Couldn't launch Steam game! oh no")
            return False

    elif gameInfo[0] == "(None,)": Popen(gameInfo[1])

# !!!MENUS!!!
menuBar = Menu(root)
menuBar.add_command(label="Scan Folder", command=scanWindow)
menuBar.add_command(label="Steam", command=steamWindow)
# Add menu to root window
root.config(menu=menuBar)



# !!!BUTTON!!!
runButton = Button(root, text="Run", command=runGame)
runButton.grid(column=0, row=10, sticky=S+W)

update()
root.mainloop()
conn.close()
