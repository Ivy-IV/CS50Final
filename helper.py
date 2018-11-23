from pathlib import Path
from urllib.request import *
import json
from sqlite3 import *
import keyring

conn = connect('launcher.db')
db = conn.cursor()

def search(path):
    """ Search folder and subfolders for .exe files and return them in a list """
    # Convert string to path object
    jeff = Path(path)
    # Get list of every exe in the path folder + its subfolders
    joff = jeff.glob('**/*.exe')

    return joff

def steamSearch(dirPaths):
    """Search Steam folders for list of installed apps, return their names and IDs"""
    for i in dirPaths:
        sL = []
        iPath = Path(i)
        appsPath = iPath.glob('steamapps/*.acf')
        for j in appsPath:
            with open(j) as k:
                acfFile = ""
                while "appid" not in acfFile:
                    acfFile = k.readline()
                sAppID = acfFile.replace('\"appid\"', '').strip('\n\t\" ')
                while "name" not in acfFile:
                    acfFile = k.readline()
                sName = acfFile.replace('\"name\"', '').strip('\n\t\" ')
            sL.append((sAppID, sName, 'steam',))
    return sL

def steamGetList():
    """ Get list of all Steam games and add them to a table in launcher.db """
    try:
        steamGet = urlopen("http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json").read()
    except:
        print("couldn't connect to steam api!")
        return False
    try:
        steamJSON = json.loads(steamGet, encoding="UTF-8")["applist"]["apps"]
    except:
        print("hey the json didn't encode")
        return False

    for i in steamJSON:
        rows = db.execute("INSERT or IGNORE INTO steamlist(appid, name) VALUES (?, ?)", (i["appid"], i["name"]))

    conn.commit()

    return True

def setLogin(prev, serv, unam, pword):
    """Sets login info for a given games service"""
    old = keyring.get_password(serv, unam)
    if old == prev or not old:
        keyring.set_password(serv, name, pword)
        return True
    else:
        print("couldn't change password!")
        return False
