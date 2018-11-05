from pathlib import Path

def search(path):
    """ Search folder and subfolders for .exe files and return them in a list """
    # Convert string to path object
    jeff = Path(path)
    # Get list of every exe in the path folder + its subfolders
    joff = jeff.glob('**/*.exe')

    return joff

def steamSearch():
    """ Get list of all Steam games and add them to a table in launcher.db """
    print("TODO")
