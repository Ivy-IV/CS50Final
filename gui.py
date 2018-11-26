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
import keyring

steamLog = False;
steamUser = ""
conn = connect('launcher.db')
db = conn.cursor()

root = Tk()
root.title("IVyVI Game Launcher")
root.geometry("800x600")
root.grid_columnconfigure(index=0, weight=1)
root.grid_columnconfigure(index=2, weight=1)
root.grid_rowconfigure(index=0, weight=1)


# !!!GAME LISTS!!!
ndLabel = Label(root, text="No DRM")
ndScrolly = Scrollbar(root)
ndScrolly.grid(column=1, row=0, sticky=NS + W)
ndScrollx = Scrollbar(root, orient=HORIZONTAL)
ndScrollx.grid(column=0, row=1, sticky=EW)
noDrmList = Listbox(root, selectmode=MULTIPLE,
yscrollcommand=ndScrolly.set, xscrollcommand=ndScrollx.set)
noDrmList.grid(column=0, row=0, sticky=EW+NS,)
ndScrolly.config(command=noDrmList.yview)
ndScrollx.config(command=noDrmList.xview)

stLabel = Label (root, text="Steam")
stScrolly = Scrollbar(root)
stScrolly.grid(column=3, row=0, sticky=NS)
stScrollx = Scrollbar(root, orient=HORIZONTAL)
stScrollx.grid(column=2, row=1, sticky=EW)
steamList = Listbox(root, selectmode=MULTIPLE,
yscrollcommand=stScrolly.set, xscrollcommand=stScrollx.set)
steamList.grid(column=2, row=0, sticky=EW+NS,)
stScrolly.config(command=steamList.yview)
stScrollx.config(command=steamList.xview)

# !!!FUNCTIONS!!!
def update():
    noDrmList.delete(0, END)
    rows = db.execute("SELECT * FROM games ORDER BY name")
    for i in rows:
        if i[1] == 'none':
            game = i[0], i[2]
            noDrmList.insert(END, game)
        elif i[1] == 'steam':
            steamList.insert(END, i[0])
    if steamList.size() > 0 or noDrmList.size() > 0: runButton.config(state=NORMAL)
    else: runButton.config(state=DISABLED)

def listEdit(command, list):
    if command == "add":
        path = filedialog.askdirectory()
        if path not in [i for i in list.get(0, END)]:
            list.insert(END, path)
            return True
        else: return False
    elif command == "remove":
        list.delete(list.curselection())
        return True

def gameDelete(listb):
    select = listb.curselection()
    for i in select:
        j = listb.get(i)
        rows = db.execute("DELETE FROM games WHERE pathid=?", (j[1],))
    listb.delete(select[0], select[-1])
    conn.commit()


    return True

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
            noDInfo = [Path(path).stem, path, 'none',]
            rows = db.execute("SELECT pathid FROM games WHERE pathid=?", (path,))
            # Returns generator object --- need to use result in condition
            if path not in rows.fetchall():
                rows = db.execute("INSERT OR REPLACE INTO games('name', 'pathid', drm) VALUES(?, ?, ?)",
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

    def userAdd():
        user = Toplevel(steam)
        labelPrev = Label(user, text="Old Password:")
        labelUser = Label(user, text="Username:").grid(column=0, row=1)
        enterUser = Entry(user).grid(column=1, row=1, sticky=EW)
    userLabel = Label(steam, text="Username: " + steamUser)

    def steamAdd():
        sList = steamSearch(steamDirList.get(0,END))
        for i in sList:
            rows = db.execute("SELECT pathid FROM games WHERE pathid=?", (i[0],))
            if i[0] not in rows.fetchall():
                ins = db.execute("INSERT OR REPLACE INTO games(pathid, name, drm) VALUES(?, ?, ?)", i)
        return True


    def steamQuit(command):
        if command == "ok":
            steamAdd()
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



    dirAddButton = Button(steam, text="Add Steam Directory", command=lambda:listEdit("add", steamDirList))
    dirAddButton.grid(row=2, sticky=NE)
    dirRemButton = Button(steam, text="Remove Steam Directory", command=lambda:listEdit("remove", steamDirList))
    dirRemButton.grid(row=2)
    steamButton = Button(steam, text="Update Steam List", command=steamAdd)
    steamButton.grid(column=1, row=4)
    okButton = Button(steam, text="OK", width=10, command=lambda: steamQuit("ok"))
    okButton.grid(column=1, row=10, sticky=SE)
    cancelButton = Button(steam, text="Cancel", width=10, command=lambda: steamQuit("cancel"))
    cancelButton.grid(column=0, row=10, sticky=SE)


def runGame(list):
    runName = list.get(ACTIVE)[0]
    print(runName)
    rows = db.execute("SELECT drm, pathid FROM games WHERE name=?", (runName,))
    gameInfo = rows.fetchone()
    if gameInfo[0] == "(steam,)":
        # Check if Steam is running - found via:
        # https://stackoverflow.com/questions/25545937/check-if-process-is-running-in-windows-using-only-python-built-in-modules
        """ !!!!!!!Maybe to be abandoned!!!!!!!
        if steamLog == False:
            checkNo = 0
            steamCheck = Popen('tasklist', shell=True).strip().split('\n')
            for line in steamCheck:
                if "steamwebhelper.exe" in line: checkNo += 1
            print(steamCheck)
            return False
            if checkNo => 3:
                steamCheck = True
                steamLog = True
            else: steamCheck = False
            if steamCheck == False:
                try: run(steamPath, "-login", steamUser, steamPass)
                except:
                    print("Login failed! oopsy")
                    return False
            steamLog = True
            """

        try: run(steamPath, "-applaunch", gameInfo[2])
        except:
            print("Couldn't launch Steam game! oh no")
            return False

    elif gameInfo[0] == "(none,)": Popen(gameInfo[1])

# !!!MENUS!!!
menuBar = Menu(root)
menuBar.add_command(label="Scan Folder", command=scanWindow)
menuBar.add_command(label="Steam", command=steamWindow)
# Add menu to root window
root.config(menu=menuBar)

def listSelect(event):
    runButton.config(command=lambda:runGame(event.widget))
    mainRemButton.config(command=lambda:gameDelete(event.widget))

# !!!BUTTONS!!!

steamList.bind("<FocusIn>", listSelect)
noDrmList.bind("<FocusIn>", listSelect)
runButton = Button(root, text="Run", command=runGame, height=2, width=15)
runButton.grid(column=0, row=10, sticky=S+W)
if steamList.size() > 0 or noDrmList.size() > 0: runButton.config(state=NORMAL)
else: runButton.config(state=DISABLED)
mainRemButton = Button(root, text="Remove From List")
mainRemButton.grid(column=1, row=10, sticky=W)

update()
root.mainloop()
conn.close()
