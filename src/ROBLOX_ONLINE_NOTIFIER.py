# coding: iso-8859-1 -*-
import json
import requests
from bs4 import BeautifulSoup
from copy import copy
from time import sleep
from random import randrange
from itertools import zip_longest
import re as regex
from farbprinter.farbprinter import Farbprinter
import os
windowsrechner = os.name == "nt"
from win10toast import ToastNotifier
toaster = ToastNotifier()
import configparser

benutzernamen = []
config = configparser.ConfigParser()
config.read("roblox_online_notifier.ini")
blink_how_often = int(str(config["CONFIG"]["blink_how_often"]).strip())
stay_for_n_seconds_each_blink = int(
    config["CONFIG"]["each_blinking_how_many_seconds"].strip(""""' """)
)
for indi, sect in enumerate(config.sections()):
    if sect.startswith("PLAYER_"):
        benutzernamen.append(config[sect]["username"].strip(""""' """))
drucker = Farbprinter()
alle = []
print("\n" * 100)
for benutzer in benutzernamen:
    jsoninhalt = requests.get(
        f"https://api.roblox.com/users/get-by-username?username={benutzer}"
    )
    j = json.loads(jsoninhalt.text)
    idnummer = j["Id"]
    accountlink = f"https://www.roblox.com/users/{idnummer}/profile"
    print(f"Getting Ids: {benutzer} : {idnummer} : {accountlink}")
    alle.append((accountlink, benutzer))
while True:
    try:
        ergebnis = []
        bereitzumsuchen = []
        for jeder in alle:
            jsoninhalt = requests.get(jeder[0])
            jsoninhalt2 = copy(jsoninhalt)
            bereitzumsuchen.append(
                [jeder, BeautifulSoup(jsoninhalt2.text, features="html.parser")]
            )
            del jsoninhalt2
            sleep(randrange(1, 8))
        for fe in bereitzumsuchen:
            status_abfragen = fe[1].findAll("span")
            for ini, fund in enumerate(status_abfragen):
                ergebnis.append([fe[0], fund])
        schon_gecheckt = []
        for einzelne_accounts in zip_longest(ergebnis):
            if einzelne_accounts[0][0][1] not in schon_gecheckt:
                print(f"Checking: {einzelne_accounts[0][0][1]}")
            schon_gecheckt.append(einzelne_accounts[0][0][1])
            for ganz in einzelne_accounts:
                spieltgerade = regex.findall(r"profile-avatar-status", str(ganz))
                if any(spieltgerade):
                    istonline = regex.findall(r"icon-online", str(ganz))
                    if any(istonline):
                        onlinemeldung = str(
                            einzelne_accounts[0][0][1]
                            + " is online:   "
                            + str(einzelne_accounts[0][0][0])
                        )

                        drucker.p.blue.black.italic(onlinemeldung)
                        for x in range(blink_how_often):
                            toaster.show_toast(title=f"{einzelne_accounts[0][0][1]} is online", msg=f"{einzelne_accounts[0][0][0]}", icon_path=r"robloxonline.ico",
                                duration=stay_for_n_seconds_each_blink,
                                threaded=False,
                            )
                    if not any(istonline):
                        onlinemeldung = str(
                            einzelne_accounts[0][0][1]
                            + " is playing:   "
                            + str(einzelne_accounts[0][0][0])
                        )
                        drucker.p.green.black.italic(onlinemeldung)
                        for x in range(blink_how_often):
                            toaster.show_toast(title=f"{einzelne_accounts[0][0][1]} is playing", msg=f"{einzelne_accounts[0][0][0]}", icon_path=r"roblox_playing.ico",
                                duration=stay_for_n_seconds_each_blink,
                                threaded=False,
                            )
        sleep(randrange(60, 120))
    except Exception as Fehler:
        drucker.p.brightred.black.italic(f"There is something wrong: {Fehler}")
        sleep(randrange(60, 120))
        continue


