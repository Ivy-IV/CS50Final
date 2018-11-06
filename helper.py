from pathlib import Path
from urllib.request import *
import json
from sqlite3 import *

conn = connect('launcher.db')
db = conn.cursor()

def search(path):
    """ Search folder and subfolders for .exe files and return them in a list """
    # Convert string to path object
    jeff = Path(path)
    # Get list of every exe in the path folder + its subfolders
    joff = jeff.glob('**/*.exe')

    return joff

def steamGetList():
    """ Get list of all Steam games and add them to a table in launcher.db """
    try:
        steamGet = urlopen("http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json").read()
    except:
        print("couldn't connect to steam api!")
        return None
    try:
        steamJSON = json.loads(steamGet, encoding="UTF-8")["applist"]["apps"]
    except:
        print("hey the json didn't encode")
        return None

    for i in steamJSON:
        rows = db.execute("INSERT or IGNORE INTO steamlist(appid, name) VALUES (?, ?)", (i["appid"], i["name"]))

    conn.commit()
