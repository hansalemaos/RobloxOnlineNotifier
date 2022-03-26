import os
import sys
def get_file_path(datei):
    pfad = sys.path
    if os.name == "nt":
        pfad = [x.replace("/", "\\") + "\\" + datei for x in pfad]
        exists = []
        for p in pfad:
            if os.path.exists(p):
                exists.append(p)
        exists = [x.replace("/", "\\") for x in exists]
        return list(dict.fromkeys(exists))
    if os.name != "nt":
        pfad = [x.replace("\\", "/") + "/" + datei for x in pfad]
        exists = []
        for p in pfad:
            if os.path.exists(p):
                exists.append(p)
        exists = [x.replace("\\", "/") for x in exists]
        return list(dict.fromkeys(exists))