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
    folder = Path(path)
    # Get list of every exe in the path folder + its subfolders
    exeList = jeff.glob('**/*.exe')

    return exeList

def steamSearch(dirPaths):
    """Search Steam folders for list of installed apps, return their names and IDs"""
    sL = []
    for i in dirPaths:
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
            if sAppID == "228980":
                break
            sL.append((sAppID, sName, 'steam',))
    return sL

def setLogin(unam, pword, prev, serv, json):
    """Sets login info for a given games service"""
    old = keyring.get_password(serv, unam)
    if old == prev or old == None:
        keyring.set_password(serv, unam, pword)
        return True
    else:
        return "Old password given didn't match saved password!"

def clearLogin(serv, unam):
    keyring.delete_password(serv, unam)
    return True
