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
from subprocess import run, Popen
from multiprocessing import Process
import keyring
import json

with open("user.json", 'r') as userfile:
    users = json.load(userfile)
print(users)

conn = connect('launcher.db')
db = conn.cursor()

root = Tk()
root.title("IVyVI Game Launcher")
root.geometry("800x600")
root.grid_columnconfigure(index=0, weight=1)
root.grid_columnconfigure(index=2, weight=1)
root.grid_rowconfigure(index=1, weight=1)


# !!!GAME LISTS!!!
ndLabel = Label(root, text="No DRM").grid()
ndScrolly = Scrollbar(root)
ndScrolly.grid(column=1, row=1, sticky=NS + W)
ndScrollx = Scrollbar(root, orient=HORIZONTAL)
ndScrollx.grid(column=0, row=2, sticky=EW)
noDrmList = Listbox(root, selectmode=EXTENDED,
yscrollcommand=ndScrolly.set, xscrollcommand=ndScrollx.set)
noDrmList.grid(column=0, row=1, sticky=EW+NS,)
ndScrolly.config(command=noDrmList.yview)
ndScrollx.config(command=noDrmList.xview)

stLabel = Label (root, text="Steam").grid(column=2, row=0)
stScrolly = Scrollbar(root)
stScrolly.grid(column=3, row=1, sticky=NS)
stScrollx = Scrollbar(root, orient=HORIZONTAL)
stScrollx.grid(column=2, row=2, sticky=EW)
steamList = Listbox(root, selectmode=EXTENDED,
yscrollcommand=stScrolly.set, xscrollcommand=stScrollx.set)
steamList.grid(column=2, row=1, sticky=EW+NS,)
stScrolly.config(command=steamList.yview)
stScrollx.config(command=steamList.xview)

# !!!FUNCTIONS!!!
def gameUpdate():
    noDrmList.delete(0, END)
    steamList.delete(0, END)
    rows = db.execute("SELECT * FROM games ORDER BY LOWER(name)")
    for i in rows:
        if i[1] == 'none':
            game = i[0]
            noDrmList.insert(END, game)
        elif i[1] == 'steam':
            steamList.insert(END, i[0])
    if steamList.size() > 0 or noDrmList.size() > 0: runButton.config(state=NORMAL)
    else: runButton.config(state=DISABLED)
    with open("user.json", 'w') as newUser:
        json.dump(users, newUser)

def listEdit(command, list):
    if command == "add":
        path = filedialog.askdirectory()
        if path not in [i for i in list.get(0, END)]:
            list.insert(END, path)
            return True
        else: return False
    elif command == "remove":
        select = list.curselection()
        list.delete(select[0], select[-1])
        return True

def gameDelete(listb):
    select = listb.curselection()
    selget = []
    selget.append(listb.get(select[0], select[-1]))
    for i in selget:
        rows = db.execute("DELETE FROM games WHERE name=?", i)
    listb.delete(select[0], select[-1])
    conn.commit()
    return True

def errorMessage(parent, message):
    error = Toplevel(parent)
    error.grab_set()
    error.title("Uh oh!")
    labelError = Label(error, text=message, pady=5, padx=5, relief=RAISED).grid(sticky=NW+SE)
    buttonError = Button(error, text="OK", command=error.destroy).grid(row=1, sticky=NW+SE)

"""!!!!!!Search for games!!!!!!"""
def scanWindow():
    scan = Toplevel(root)
    scan.title("Scan Folder")
    scan.geometry("800x430")
    scan.grid_columnconfigure(index=0, weight=1)
    scan.grab_set()

    """!!!!!!Games with no digital management!!!!!!"""
    noDrmLabel = Label(scan, text="No DRM/Digital Service", height=2).grid(columnspan=2)
    noDrmFrame = Frame(scan)
    noDrmFrame.grid(columnspan=2, row=1, sticky=NW+SE)
    noDrmFrame.grid_columnconfigure(index=1, weight=1)
    noDrmFrame.grid_columnconfigure(index=5, weight=1)
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
                if Path(item) not in [Path(i) for i in leaveList.get(0, END)]: leaveList.insert(END, item)

        return True
    def listSwap(command):
        lists = (addList, leaveList) if command == "add" else (leaveList, addList)
        select = lists[1].curselection()
        for j in reversed(select):
            lists[0].insert(0, lists[1].get(j))
            lists[1].delete(j)

    def addNoDRM():
        select = addList.curselection()
        for i in select:
            path = addList.get(i)
            noDInfo = [Path(path).stem, path, 'none',]
            rows = db.execute("SELECT pathid FROM games WHERE pathid=?", (path,))
            if path not in rows.fetchall():
                rows = db.execute("INSERT OR REPLACE INTO games('name', 'pathid', drm) VALUES(?, ?, ?)",
                    noDInfo)
        conn.commit()
        gameUpdate()
        return True

    # !!!LIST!!!
    leaveScrolly = Scrollbar(noDrmFrame)
    leaveScrolly.grid(column=3, rowspan=2, sticky=NS)
    leaveScrollx = Scrollbar(noDrmFrame, orient=HORIZONTAL)
    leaveScrollx.grid(column=1, columnspan=2, row=2, sticky=EW)
    leaveList = Listbox(noDrmFrame, selectmode=MULTIPLE,
    yscrollcommand=leaveScrolly.set, xscrollcommand=leaveScrollx.set)
    leaveList.grid(column=1, columnspan=2, row=0, rowspan=2, sticky=EW+NS,)
    leaveScrolly.config(command=leaveList.yview)
    leaveScrollx.config(command=leaveList.xview)

    scrolly = Scrollbar(noDrmFrame)
    scrolly.grid(column=7, row=0, rowspan=2, sticky=NS)
    scrollx = Scrollbar(noDrmFrame, orient=HORIZONTAL)
    scrollx.grid(column=5, columnspan=2, row=2, sticky=EW)
    addList = Listbox(noDrmFrame, selectmode=MULTIPLE,
    yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
    addList.grid(column=5, columnspan=2, row=0, rowspan=2, sticky=EW+NS,)
    scrolly.config(command=addList.yview)
    scrollx.config(command=addList.xview)
    # !!!BUTTONS!!!
    fileButton = Button(noDrmFrame, text="Select File", command=lambda: getList(0))
    fileButton.grid(column=0, row=0, sticky=N+EW)
    folderButton = Button(noDrmFrame, text="Scan Folder", command=lambda: getList(1))
    folderButton.grid(column=0, row=1, sticky=N+EW)
    addButton = Button(noDrmFrame, width=6, text="Add\n-->", command=lambda:listSwap("add"))
    addButton.grid(column=4, row=0)
    remButton = Button(noDrmFrame, text="Remove\n<--", command=lambda:listSwap("remove"))
    remButton.grid(column=4, row=1)

    """!!!!!!Steam Games!!!!!!"""
    steamLabel = Label(scan, text="Steam Games").grid(row=2,columnspan=2)
    steamFrame = Frame(scan)
    steamFrame.grid(columnspan=2, row=3, sticky=NW+SE)
    steamFrame.grid_columnconfigure(index=1, weight=1)

    def userAdd():
        user = Toplevel()
        user.title("Set Steam User")
        user.grab_set()

        def userOK():
            if enterPrev is not None:
                prev = enterPrev.get()
            else:
                prev = ""
            attempt = setLogin(enterUser.get(), enterPass.get(), prev, "steam", users)
            if attempt is not True:
                errorMessage(user, attempt)
                return False
            else:
                users["steam"]["user"] = enterUser.get()
                userLabel.config(text="Current: {}".format(users["steam"]["user"]))
                print(users)
                gameUpdate()
                scan.destroy()
                return True

        def userClear(service, unam):
            clearLogin(server, unam)
            users["steam"]["user"] = ""
            users["steam"]["path"] = ""
            userLabel.config(text="Current: {}".format(users["steam"]["user"]))
            gameUpdate()
            return True

        labelPrev = Label(user, text="Old Password:")
        labelPrev.grid(row=0)
        enterPrev = Entry(user, show='*')
        enterPrev.grid(column=1, row=0, sticky=EW)
        labelUser = Label(user, text="Username:").grid(column=0, row=1)
        enterUser = Entry(user)
        enterUser.grid(column=1, row=1, sticky=EW)
        passVar = StringVar()
        labelPass = Label(user, text="Password:").grid(row=2)
        enterPass = Entry(user, textvariable=passVar, show='*')
        enterPass.grid(column=1, row=2, sticky=EW)
        buttonOK = Button(user, text="OK", command=userOK).grid(columnspan=2, row=3)
        buttonClear = Button(user, text="Clear Login", command=lambda:userClear(steam, users[steam]))

    def steamAdd():
        sList = steamDirList.get(0,END)
        for i in steamSearch(sList):
            rows = db.execute("SELECT pathid FROM games WHERE pathid=?", (i[0],))
            if i[0] not in rows.fetchall():
                ins = db.execute("INSERT OR REPLACE INTO games(pathid, name, drm) VALUES(?, ?, ?)", i)
            for i in sList:
                if Path(i, 'Steam.exe').exists():
                    users["steam"]["path"] = i + '/Steam.exe'
        return True

    def steamQuit(command):
        if command == "ok":
            steamAdd()
            addNoDRM()
            conn.commit()
            gameUpdate()
        elif command == "cancel":
            conn.rollback()
        scan.destroy()

    #!!!!!LIST!!!!!
    steamScry = Scrollbar(steamFrame)
    steamScry.grid(column=3, row=2, sticky=NS)
    steamScrx = Scrollbar(steamFrame, orient=HORIZONTAL)
    steamScrx.grid(column=1, columnspan=2, row=3, sticky=EW)
    steamDirList = Listbox(steamFrame, selectmode=MULTIPLE, height=5,
    yscrollcommand=steamScry.set, xscrollcommand=steamScrx.set)
    steamDirList.grid(column=1, columnspan=2, row=2, sticky=EW+NS,)
    steamScry.config(command=steamDirList.yview)
    steamScrx.config(command=steamDirList.xview)

    userButton = Button(steamFrame, text="Change User", command=userAdd)
    userButton.grid(row=0)
    userLabel = Label(steamFrame, text="Current: {}".format(users["steam"]["user"]))
    userLabel.grid(column=1, row=0, sticky=W)
    dirLabel = Label(steamFrame, text="Steam Launcher Location: {}".format(users["steam"]["path"]))
    dirLabel.grid(row=1, columnspan=2, sticky=W)
    dirAddButton = Button(steamFrame, text="Add Steam Directory", command=lambda:listEdit("add", steamDirList))
    dirAddButton.grid(row=2, sticky=NE)
    dirRemButton = Button(steamFrame, text="Remove Steam Directory", command=lambda:listEdit("remove", steamDirList))
    dirRemButton.grid(row=2)
    okButton = Button(scan, text="OK", width=10, command=lambda:steamQuit("ok"))
    okButton.grid(column=1, row=10, sticky=SE)
    cancelButton = Button(scan, text="Cancel", width=10, command=lambda:steamQuit("cancel"))
    cancelButton.grid(column=0, row=10, sticky=SE)

def runGame(list):
    runName = list.get(ACTIVE)
    rows = db.execute("SELECT drm, pathid FROM games WHERE name=?", (runName,))
    gameInfo = rows.fetchone()
    if gameInfo[0] == "steam":
            try:
                Popen([users["steam"]["path"], "-login", users["steam"]["user"],
                    keyring.get_password("steam", users["steam"]["user"]),
                    "-applaunch", gameInfo[1]], shell=True)
                return True
            except FileNotFoundError:
                errorMessage(root, "Steam.exe not found at\n{}".format(users["steam"]["path"]))
                return False

    elif gameInfo[0] == "none":
        try:
            Popen(gameInfo[1], shell=True)
            return True
        except FileNotFoundError:
            errorMessage(root, "File at \n{}\n not found!".format(gameInfo[1]))
            gameDelete(list)

# !!!MENUS!!!
menuBar = Menu(root)
menuBar.add_command(label="Search for Games", command=scanWindow)
# Add menu to root window
root.config(menu=menuBar)

# !!!EVENT HANDLERS!!!
def listSelect(event):
    runButton.config(command=lambda:runGame(event.widget))
    mainRemButton.config(command=lambda:gameDelete(event.widget))
def doubleClick(event):
    runGame(event.widget)
def deleteList(event):
    selection = event.widget.curselection()
    event.widget.delete(selection[0], selection[-1])
def deleteGame(event):
    gameDelete(event.widget)
# !!!BUTTONS!!!
steamList.bind("<FocusIn>", listSelect)
noDrmList.bind("<FocusIn>", listSelect)
steamList.bind("<Double-Button-1>", doubleClick)
noDrmList.bind("<Double-Button-1>", doubleClick)
steamList.bind("<Delete>", deleteGame)
noDrmList.bind("<Delete>", deleteGame)
root.bind_class("Listbox", "<Delete>", deleteList)
runButton = Button(root, text="Run", height=2, width=15)
runButton.grid(column=0, row=10, sticky=S+W)
if steamList.size() > 0 or noDrmList.size() > 0: runButton.config(state=NORMAL)
else: runButton.config(state=DISABLED)
mainRemButton = Button(root, text="Remove From List")
mainRemButton.grid(column=2, row=10, sticky=E)

gameUpdate()
root.mainloop()
conn.close()
