from kivy.config import Config
Config.set("kivy", "exit_on_escape", "0")
import os
import sys
from collections import defaultdict
import webbrowser
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineListItem
from kivy.core.window import Window
import json
import requests
from bs4 import BeautifulSoup
from itertools import zip_longest
from copy import copy
from time import time
import kthread
import re
import configparser


debug = False
pathoffile = re.sub(r"[\\/][^\\/]+$", "", __file__)
sys.path.append(pathoffile)
iswindows = os.name == "nt"

if not iswindows:
    if not os.path.exists(pathoffile + "/win10toast"):
        os.makedirs(pathoffile + "/win10toast")
        with open(
            pathoffile + "/win10toast/__init__.py", mode="w", encoding="utf-8"
        ) as f:
            f.write("class ToastNotifier:\n    pass\n")

if iswindows:
    try:
        from win10toast import ToastNotifier

        toaster = ToastNotifier()
    except Exception as Fehler:
        if debug:
            print("Not a Windows PC")


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


def create_nested_dict():
    nested_dict = lambda: defaultdict(nested_dict)
    return nested_dict()


class MainApp(MDApp):
    config = configparser.ConfigParser()
    configfile = get_file_path("robloxconfig.ini")[0]
    config.read(configfile)
    appname = "Roblox Online Notifier"
    kv_file = get_file_path("r_online_checker.kv")[0]
    accountfile = get_file_path("robloxaccountschecken.txt")[0]
    accountfile_mit_ids = get_file_path("robloxaccountschecken_ids.txt")[0]
    playingicon = get_file_path("roblox_playing.ico")[0]
    edit_account_text = "Edit Account File"
    edit_account_text_save = "Save Account File"
    update_time_input = int(str(config["DEFAULT"]["update_time_input"]).strip())
    textinput_blink_how_often = int(
        str(config["DEFAULT"]["textinput_blink_how_often"]).strip()
    )
    textinput_blink_how_many_seconds = int(
        str(config["DEFAULT"]["textinput_blink_how_many_seconds"]).strip()
    )
    robloxids = {}
    roblox_accounts_zum_checken = create_nested_dict()
    last_checked_accounts = []
    scheduled_actions = []
    accountcolor_offline = (1, 1, 1, 0.5)
    accountcolor_online = (1, 1, 1, 1)
    accountcolor_offline_secondary = (1, 0, 0, 1)
    accountcolor_online_secondary = (0, 1, 0, 1)
    robloxidcolor = (1, 1, 0, 0.5)
    account_online_text = "Account is online"
    account_offline_text = "Account is offline"
    check_account_loop = True
    after_update_clock = []

    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        self.title = self.appname
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.secondary_palette = "Green"
        self.read_roblox_id_file()
        Clock.schedule_once(self.disable_toast_if_not_windows)
        Clock.schedule_once(self.hide_text_box)
        self.after_update_clock.append(
            Clock.schedule_interval(self.get_update_roblox_list, self.update_time_input)
        )
        self.after_update_clock.append(
            Clock.schedule_interval(self.up_date_list, self.update_time_input)
        )
        if iswindows:
            t = kthread.KThread(target=self.wintoast_anzeigen, name="showtoast")
            t.start()
        return Builder.load_file(self.kv_file)

    def on_request_close(self, *args):
        self.check_account_loop = False

    def disable_toast_if_not_windows(self, *args):
        if not iswindows:
            self.root.ids.switch_show_toast_notification.active = False
            self.hide_widget(self.root.ids.switch_show_toast_notification)
            self.hide_widget(self.root.ids.label_show_windows_notification)
            self.hide_widget(self.root.ids.label_blink_often)
            self.hide_widget(self.root.ids.textinput_blink_how_often)
            self.hide_widget(self.root.ids.label_blink_how_many_seconds)
            self.hide_widget(self.root.ids.textinput_blink_how_many_seconds)

    def up_date_list(self, *args):
        self.root.ids.MDList_1.clear_widgets()
        if any(list(self.roblox_accounts_zum_checken.keys())):
            for account in self.roblox_accounts_zum_checken.keys():
                if self.roblox_accounts_zum_checken[account]["online"]:
                    if debug:
                        print(
                            "online:" + str(self.roblox_accounts_zum_checken[account])
                        )
                    self.root.ids.MDList_1.add_widget(
                        ThreeLineListItem(
                            text=account,
                            secondary_text=self.account_online_text,
                            text_color=self.accountcolor_online,
                            theme_text_color="Custom",
                            secondary_theme_text_color="Custom",
                            secondary_text_color=self.accountcolor_online_secondary,
                            tertiary_text=self.roblox_accounts_zum_checken[account][
                                "id"
                            ],
                            tertiary_theme_text_color="Custom",
                            tertiary_text_color=self.robloxidcolor,
                            on_release=lambda x: self.open_account_in_webbrowser(x),
                        )
                    )
                elif not self.roblox_accounts_zum_checken[account]["online"]:
                    if debug:
                        print(
                            "Nicht online:"
                            + str(self.roblox_accounts_zum_checken[account])
                        )
                    self.root.ids.MDList_1.add_widget(
                        ThreeLineListItem(
                            text=account,
                            secondary_text=self.account_offline_text,
                            text_color=self.accountcolor_offline,
                            theme_text_color="Custom",
                            secondary_theme_text_color="Custom",
                            secondary_text_color=self.accountcolor_offline_secondary,
                            tertiary_text=self.roblox_accounts_zum_checken[account][
                                "id"
                            ],
                            tertiary_theme_text_color="Custom",
                            tertiary_text_color=self.robloxidcolor,
                            on_release=lambda x: self.open_account_in_webbrowser(x),
                        )
                    )

    def wintoast_anzeigen(self):
        while self.check_account_loop:
            try:
                if self.root.ids.switch_show_toast_notification.active:
                    for account in self.roblox_accounts_zum_checken.keys():
                        if self.roblox_accounts_zum_checken[account]["online"]:
                            if debug:
                                print(f"{account} is online")
                            for x in range(
                                int(self.root.ids.textinput_blink_how_often.text)
                            ):
                                if self.root.ids.switch_show_toast_notification.active:
                                    toaster.show_toast(
                                        title=f"{account}",
                                        msg=f"{account} is online/playing",
                                        icon_path=self.playingicon,
                                        duration=int(
                                            self.root.ids.textinput_blink_how_many_seconds.text
                                        ),
                                        threaded=False,
                                    )
                elif not self.root.ids.switch_show_toast_notification.active:
                    if debug:
                        print("is aus")
                # sleep(.3)
            except Exception as Fehler:
                if debug:
                    print(Fehler)
                # sleep(.3)

    def open_account_in_webbrowser(self, *args):
        webbrowser.open(
            fr"""https://web.roblox.com/users/{self.robloxids[args[0].text]}/profile"""
        )

    def hide_text_box(self, *args):
        self.hide_widget(self.root.ids.add_accounts, dohide=True)

    def read_txt_file(self, textfile, liste=True):
        with open(textfile, mode="r", encoding="utf-8") as f:
            data = f.readlines()
        if liste:
            return [str(x).strip() for x in data]
        return "\n".join([str(x).strip() for x in data]).strip()

    def write_txt_file(self, data, textfile):
        if isinstance(data, list):
            data = "\n".join(data).strip()
        with open(textfile, mode="w", encoding="utf-8") as f:
            f.write(data.strip())

    def read_roblox_id_file(self):
        robloxaccountlist = [
            re.split(r"\s*,\s*", x)
            for x in self.read_txt_file(textfile=self.accountfile_mit_ids, liste=True)
        ]
        for account in robloxaccountlist:
            self.robloxids[account[0]] = account[1]
        if debug:
            print(self.robloxids)

    def get_roblox_id_update_roblox_id_file(self, account):
        try:
            jsoninhalt = requests.get(
                f"https://api.roblox.com/users/get-by-username?username={account}"
            )
            j = json.loads(jsoninhalt.text)
            self.robloxids[account] = str(j["Id"])
        except:
            self.robloxids[account] = "Account does not exist!"
        liste = []
        for k, v in self.robloxids.items():
            liste.append(f"{k},{v}")
        self.write_txt_file(data=liste, textfile=self.accountfile_mit_ids)

    def get_update_roblox_list(self, *args):
        if any(self.scheduled_actions):
            try:
                self.scheduled_actions[-1].cancel()
            except Exception as Fehler:
                if debug:
                    print(Fehler)
        account_with_smallest_date = []
        for account in self.roblox_accounts_zum_checken.keys():
            account_with_smallest_date.append(
                self.roblox_accounts_zum_checken[account]["last_checked"]
            )
        account_with_smallest_date.sort()
        accounts2check = self.read_txt_file(textfile=self.accountfile, liste=True)
        for account in accounts2check:
            if account not in self.roblox_accounts_zum_checken.keys():
                self.roblox_accounts_zum_checken[account][
                    "online"
                ] = self.check_if_account_online(
                    accountnummer=self.robloxids[account], accountname=account
                )
                self.roblox_accounts_zum_checken[account]["id"] = self.robloxids[
                    account
                ]
                self.roblox_accounts_zum_checken[account]["last_checked"] = time()
                self.last_checked_accounts.append(
                    (self.roblox_accounts_zum_checken[account]["last_checked"], account)
                )
                # hier checken ob_online
            elif account in self.roblox_accounts_zum_checken.keys():
                if (
                    self.roblox_accounts_zum_checken[account]["last_checked"]
                    == account_with_smallest_date[0]
                ):
                    self.roblox_accounts_zum_checken[account][
                        "online"
                    ] = self.check_if_account_online(
                        accountnummer=self.robloxids[account], accountname=account
                    )
                    self.roblox_accounts_zum_checken[account]["id"] = self.robloxids[
                        account
                    ]
                    self.roblox_accounts_zum_checken[account]["last_checked"] = time()
                    self.last_checked_accounts.append(
                        (
                            self.roblox_accounts_zum_checken[account]["last_checked"],
                            account,
                        )
                    )
        if debug:
            print(self.roblox_accounts_zum_checken)
        self.scheduled_actions.append(
            Clock.schedule_interval(self.constant_check, self.update_time_input)
        )

    def constant_check(self, *args):
        self.last_checked_accounts.sort()
        if debug:
            print(self.last_checked_accounts)

    def editaccountlist(self):
        if self.root.ids.open_roblox_account_list_button.text == self.edit_account_text:
            self.hide_widget(self.root.ids.add_accounts, dohide=False)
            self.root.ids.open_roblox_account_list_button.text = (
                self.edit_account_text_save
            )
            self.root.ids.add_accounts.text = self.read_txt_file(
                textfile=self.accountfile, liste=False
            )
        elif (
            self.root.ids.open_roblox_account_list_button.text
            == self.edit_account_text_save
        ):
            self.hide_widget(self.root.ids.add_accounts, dohide=True)
            self.root.ids.open_roblox_account_list_button.text = self.edit_account_text
            textzumchecken = [
                str(x).strip().replace(",", "")
                for x in str(self.root.ids.add_accounts.text).splitlines()
            ]
            for account in textzumchecken:
                if account not in self.robloxids:
                    self.get_roblox_id_update_roblox_id_file(account=account)
            self.write_txt_file(
                data=self.root.ids.add_accounts.text, textfile=self.accountfile
            )
            self.get_update_roblox_list()
            self.delete_accounts_from_searchlist()

    def delete_accounts_from_searchlist(self):
        allacco = list(self.roblox_accounts_zum_checken.keys())
        accounts2check = self.read_txt_file(textfile=self.accountfile, liste=True)
        for acco in allacco:
            if acco not in accounts2check:
                try:
                    del self.roblox_accounts_zum_checken[acco]
                except Exception as Fehler:
                    if debug:
                        print(Fehler)

    def hide_widget(self, wid, dohide=True):
        if hasattr(wid, "saved_attrs"):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True

    def set_number(self, text, number):
        if not str(number).isnumeric():
            text.text = "10"
        self.update_time_input = int(self.root.ids.update_time_input.text)
        self.textinput_blink_how_often = int(
            self.root.ids.textinput_blink_how_often.text
        )
        self.textinput_blink_how_many_seconds = int(
            self.root.ids.textinput_blink_how_many_seconds.text
        )
        with open(self.configfile, "w") as f:
            f.write(
                f"""[DEFAULT]\nupdate_time_input = {self.update_time_input}\ntextinput_blink_how_often = {self.textinput_blink_how_often}\ntextinput_blink_how_many_seconds = {self.textinput_blink_how_many_seconds}"""
            )

        for action in range(len(self.after_update_clock)):
            try:
                self.after_update_clock[action].cancel()
            except:
                continue
        self.after_update_clock.append(
            Clock.schedule_interval(self.get_update_roblox_list, self.update_time_input)
        )
        self.after_update_clock.append(
            Clock.schedule_interval(self.up_date_list, self.update_time_input)
        )

    def check_if_account_online(self, accountnummer, accountname):
        jeder = f"https://www.roblox.com/users/{accountnummer}/profile"
        try:
            ergebnis = []
            bereitzumsuchen = []
            jsoninhalt = requests.get(jeder)
            jsoninhalt2 = copy(jsoninhalt)
            bereitzumsuchen.append(
                [jeder, BeautifulSoup(jsoninhalt2.text, features="html.parser")]
            )
            for fe in bereitzumsuchen:
                status_abfragen = fe[1].findAll("span")
                for ini, fund in enumerate(status_abfragen):
                    ergebnis.append([fe[0], fund])
            schon_gecheckt = []
            for einzelne_accounts in zip_longest(ergebnis):
                if einzelne_accounts[0][0][1] not in schon_gecheckt:
                    if debug:
                        print(f"Checking: {accountname}")
                schon_gecheckt.append(einzelne_accounts[0][0][1])
                for ganz in einzelne_accounts:
                    spieltgerade = re.findall(r"profile-avatar-status", str(ganz))
                    if any(spieltgerade):
                        istonline = re.findall(r"icon-online", str(ganz))
                        if any(istonline):
                            onlinemeldung = str(accountname + " is online:   ")
                            if debug:
                                print(onlinemeldung)
                            return True
                        if not any(istonline):
                            onlinemeldung = str(accountname + " is playing:   ")
                            if debug:
                                print(onlinemeldung)
                            return True
        except Exception as Fehler:
            if debug:
                print(f"There is something wrong: {Fehler}")
            return False
        return False


if __name__ == "__main__":
    MainApp().run()
    sys.exit()
