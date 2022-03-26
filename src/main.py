import configparser
import re
import webbrowser
from itertools import zip_longest
from time import sleep, time
import certifi
from bs4 import BeautifulSoup
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineIconListItem, MDList, ThreeLineListItem
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from kivy.core.window import Window
from create_nested_dict import create_nested_dict
from exception_handler import *
from get_absolut_filepath import get_file_path
from cprint import cprint
import kthread
from os_imports import *


debug = False
appname = "RobloxOnlineNotifier"
toolbar_title = "Roblox Online Notifier"
kv_file = get_file_path("design.kv")[0]
configfile = get_file_path("robloxconfig.ini")[0]
accountfile = get_file_path("robloxaccountschecken.txt")[0]
accountfile_mit_ids = get_file_path("robloxaccountschecken_ids.txt")[0]
playingicon = get_file_path("roblox_playing.ico")[0]
app_is_closed = False
toaster = ToastNotifier()


class BoxLayout1(MDBoxLayout):
    pass


class BoxLayout2(MDBoxLayout):
    pass


class Tela0(MDScreen):
    thumbnail = StringProperty()


class Tela1(MDScreen):
    thumbnail = StringProperty()


class Tela2(MDScreen):
    thumbnail = StringProperty()


class ContentNavigationDrawer(MDBoxLayout):
    pass


class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ListProperty((0, 0, 0, 1))


class DrawerList(ThemableBehavior, MDList):
    def set_color_item(self, instance_item):
        """Called when tap on a menu item."""
        # Set the color of the icon and text for the menu item.
        for item in self.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        instance_item.text_color = self.theme_cls.primary_color


class ConfigReader:
    config = configparser.ConfigParser()
    config.read(configfile)
    update_time_input = int(str(config["DEFAULT"]["update_time_input"]).strip())
    textinput_blink_how_often = int(
        str(config["DEFAULT"]["textinput_blink_how_often"]).strip()
    )
    textinput_blink_how_many_seconds = int(
        str(config["DEFAULT"]["textinput_blink_how_many_seconds"]).strip()
    )
    text_sleeptime = int(str(config["DEFAULT"]["text_sleeptime"]).strip())
    blink_or_vibrate = bool(int(str(config["DEFAULT"]["blink_or_vibrate"]).strip()))


class RobloxChecker:
    def __init__(self, **kwargs):
        self.robloxids = create_nested_dict()
        self.roblox_accounts_zum_checken = create_nested_dict()
        self.read_roblox_id_file()
        self.read_roblox_accounts_to_search_for()
        cprint.cyan(self.robloxids)
        cprint.cyan(self.roblox_accounts_zum_checken)

    def constant_update(self):
        while not app_is_closed:
            try:
                self.read_roblox_accounts_to_search_for()
                account_with_smallest_date = self.get_check_dates()
                if not any(account_with_smallest_date):
                    self.sleeping()
                    continue
                accounts2check = list(self.roblox_accounts_zum_checken.keys())
                for account in accounts2check:
                    if (
                        self.roblox_accounts_zum_checken[account]["last_checked"]
                        == account_with_smallest_date[0]
                    ):
                        self.roblox_accounts_zum_checken[account][
                            "online"
                        ] = self.check_if_account_online(
                            accountnummer=self.roblox_accounts_zum_checken[account][
                                "id"
                            ],
                            accountname=account,
                        )
                        self.roblox_accounts_zum_checken[account][
                            "last_checked"
                        ] = time()
                        break
                cprint.green(self.roblox_accounts_zum_checken)
                self.sleeping()
            except Exception as Fehler:
                print_exception(Fehler)

    def sleeping(self):
        for x in range(FileConfig.update_time_input * 2):
            if app_is_closed:
                return True
            sleep(.5)

    def get_check_dates(self):
        account_with_smallest_date = []
        if any(list(self.roblox_accounts_zum_checken.keys())):
            for account in list(self.roblox_accounts_zum_checken.keys()):
                account_with_smallest_date.append(
                    self.roblox_accounts_zum_checken[account]["last_checked"]
                )
            account_with_smallest_date.sort()
        return account_with_smallest_date

    def read_txt_file(self, textfile):
        with open(textfile, mode="r", encoding="utf-8") as f:
            data = f.readlines()
        return [str(x).strip() for x in data]

    def read_roblox_id_file(self):
        robloxaccountlist = [
            re.split(r"\s*,\s*", x)
            for x in self.read_txt_file(textfile=accountfile_mit_ids)
        ]
        for account in robloxaccountlist:
            self.robloxids[account[0]] = account[1]
        if debug:
            print(self.robloxids)

    def read_roblox_accounts_to_search_for(self):
        accounts = self.read_txt_file(textfile=accountfile)
        if any(accounts):
            for ini, acc in enumerate(accounts):
                if acc not in self.roblox_accounts_zum_checken.keys():
                    self.roblox_accounts_zum_checken[acc]["online"] = False
                    # very small to be the next accounts to be checked for
                    self.roblox_accounts_zum_checken[acc]["last_checked"] = ini
                    if acc not in self.robloxids.keys():
                        self.get_id_of_roblox_account(acc)
                    self.roblox_accounts_zum_checken[acc]["id"] = str(
                        self.robloxids[acc]
                    )
                    cprint.blue(self.roblox_accounts_zum_checken)

    def get_id_of_roblox_account(self, account):
        url = f"https://api.roblox.com/users/get-by-username?username={account}"
        try:
            req = UrlRequest(url, ca_file=certifi.where())
            req.wait()
            if "User not found" not in str(req.__dict__["_result"]):
                self.robloxids[account] = str(req.__dict__["_result"]["Id"])
            elif "User not found" in str(req.__dict__["_result"]):
                self.robloxids[account] = "User does not exist"
        except Exception as Fehler:
            print_exception(Fehler)
        # Writes account file to save new Roblox ids right away
        with open(accountfile_mit_ids, mode="w", encoding="utf-8") as f:
            f.write("\n".join([f"{k},{v}" for k, v in self.robloxids.items()]).strip())

    def write_accounts_to_search_for(self):
        with open(accountfile, mode="w", encoding="utf-8") as f:
            f.write(
                "\n".join([k for k in self.roblox_accounts_zum_checken.keys()]).strip()
            )

    def check_if_account_online(self, accountnummer, accountname):
        jeder = f"https://www.roblox.com/users/{accountnummer}/profile"
        if str(accountnummer).isnumeric():
            try:
                ergebnis = []
                bereitzumsuchen = []
                req = UrlRequest(jeder, ca_file=certifi.where())
                req.wait()
                bereitzumsuchen.append(
                    [
                        jeder,
                        BeautifulSoup(req.__dict__["_result"], features="html.parser"),
                    ]
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
                print_exception(Fehler)
                return False
            return False


class TestNavigationDrawer(MDApp):
    thumbnail = StringProperty()

    def __init__(self, **kwargs):
        super(TestNavigationDrawer, self).__init__(**kwargs)

        self.update_time_input = FileConfig.update_time_input
        self.textinput_blink_how_often = FileConfig.textinput_blink_how_often
        self.textinput_blink_how_many_seconds = (
            FileConfig.textinput_blink_how_many_seconds
        )
        self.text_sleeptime = FileConfig.text_sleeptime
        self.blink_or_vibrate = FileConfig.blink_or_vibrate

        # read config information used in tela1
        self.title = appname

        self.space_before = "   "
        self.menutitel = ""
        self.webpagetoopen1 = "https://github.com/hansalemaos?tab=repositories"

        self.subtitlel0 = "Check online status"
        self.subtitlel1 = "Add / Remove Players"
        self.subtitlel2 = "Configuration"
        self.subtitlel3 = "About this app"

        self.icon0item = "account-check-outline"
        self.icon1item = "account-plus-outline"
        self.icon2item = "account-cog"
        self.icon3item = "alpha-i-circle-outline"

        self.robloximage0 = get_file_path("robloxlogo0.png")[0]
        self.robloximage1 = get_file_path("robloxlogo1.png")[0]
        self.robloximage2 = get_file_path("robloxlogo_config.png")[0]
        self.robloximage3 = get_file_path("robloxlogo2.png")[0]

        self.icons_item = {
            self.icon0item: self.subtitlel0,
            self.icon1item: self.subtitlel1,
            self.icon2item: self.subtitlel2,
            self.icon3item: self.subtitlel3,
        }

        # for main screen - to show if account online/offline
        self.accountcolor_offline = (0, 0, 0, 0.5)
        self.accountcolor_online = (0, 0, 0, 1)
        self.accountcolor_offline_secondary = (1, 0, 0, 1)
        self.accountcolor_online_secondary = (0, 0.5, 0, 1)
        self.robloxidcolor = (0, 0, 1, 1)
        self.account_online_text = "Account is online"
        self.account_offline_text = "Account is offline"

        # to stop start/account checks
        self.scheduled_actions = {}
        self.threaded_toasts = {}



    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        return Builder.load_file(kv_file)

    def show_toast(self, account):
        try:
            if self.blink_or_vibrate:
                if any(list(self.threaded_toasts.keys())):
                    if self.threaded_toasts["toast"].is_alive():
                        self.threaded_toasts["toast"].kill()
                    del self.threaded_toasts["toast"]
                    self.threaded_toasts["toast"] = kthread.KThread(
                        target=self.show_threaded_system_toasts,
                        name="toast",
                        args=(account,),
                    )
                    self.threaded_toasts["toast"].start()
                elif not any(list(self.threaded_toasts.keys())):
                    self.threaded_toasts["toast"] = kthread.KThread(
                        target=self.show_threaded_system_toasts,
                        name="toast",
                        args=(account,),
                    )
                    self.threaded_toasts["toast"].start()
        except Exception as Fehler:
            print_exception(Fehler)

    def show_threaded_system_toasts(self, account):
        try:
            if platform == "win":
                toaster.show_toast(
                    title=f"{account}",
                    msg=f"{account} is online/playing",
                    icon_path=playingicon,
                    duration=self.textinput_blink_how_many_seconds,
                    threaded=False,
                )
            elif platform == "ios" or platform == "android":
                vibrator.vibrate(self.textinput_blink_how_many_seconds)
            elif platform == "macosx":
                ApplescriptNotification(f"User online/playing").with_title(
                    account
                ).with_subtitle("is online").send()
            elif platform == "linux":
                sendmessage(message=f"{account} is online/playing")
        except Exception as Fehler:
            print_exception(Fehler)

    def click_on_md_switch(self, *args):
        self.blink_or_vibrate = args[0]
        RobloxAccounts.blink_or_vibrate = self.blink_or_vibrate
        self.write_config_file()

    def set_new_time_variables(self):
        FileConfig.update_time_input = self.update_time_input
        FileConfig.textinput_blink_how_often = self.textinput_blink_how_often
        FileConfig.textinput_blink_how_many_seconds = (
            self.textinput_blink_how_many_seconds
        )
        FileConfig.text_sleeptime = self.text_sleeptime
        FileConfig.blink_or_vibrate = self.blink_or_vibrate

    def write_config_file(self):
        self.set_new_time_variables()
        cprint.cyan("Configfile written")
        with open(configfile, "w") as f:
            f.write(
                f"""[DEFAULT]\nupdate_time_input = {self.update_time_input}\ntextinput_blink_how_often = {self.textinput_blink_how_often}\ntextinput_blink_how_many_seconds = {self.textinput_blink_how_many_seconds}\ntext_sleeptime = {self.text_sleeptime}\nblink_or_vibrate = {int(self.blink_or_vibrate)}"""
            )

        print(FileConfig.update_time_input)
        print(FileConfig.textinput_blink_how_often)
        print(FileConfig.textinput_blink_how_many_seconds)
        print(FileConfig.text_sleeptime)
        print(FileConfig.blink_or_vibrate)

    def gedrueckt(self, *args):
        self.root.ids.nav_drawer.set_state("close")
        cprint.green(args)
        if args[0] == self.icons_item[self.icon0item]:
            self.root.ids.screen_manager.current = ""
            self.root.ids.content_drawer.ids.sublabel.text = self.subtitlel0
            self.root.ids.content_drawer.ids.avatar.source = self.robloximage0

        if args[0] == self.icons_item[self.icon1item]:
            self.root.ids.screen_manager.current = "tela0"
            self.root.ids.content_drawer.ids.sublabel.text = self.subtitlel1
            self.root.ids.content_drawer.ids.avatar.source = self.robloximage1

        if args[0] == self.icons_item[self.icon2item]:
            self.root.ids.screen_manager.current = "tela1"
            self.root.ids.content_drawer.ids.sublabel.text = self.subtitlel2
            self.root.ids.content_drawer.ids.avatar.source = self.robloximage2

        if args[0] == self.icons_item[self.icon3item]:
            self.root.ids.screen_manager.current = "tela2"
            self.root.ids.content_drawer.ids.sublabel.text = self.subtitlel3
            self.root.ids.content_drawer.ids.avatar.source = self.robloximage3

    def open_navigationbar(self):
        self.root.ids.nav_drawer.set_state("open")

    def add_menu_items(self):
        "Ist ok hier zu definieren, da sie in der kv-datei im ItemDrawer übergeben werden können"
        for icon_name in self.icons_item.keys():
            self.root.ids.content_drawer.ids.md_list.add_widget(
                ItemDrawer(icon=icon_name, text=self.icons_item[icon_name])
            )

    def on_start(self):
        self.add_menu_items()
        self.root.ids.screen_manager.add_widget(Tela0(name="tela0"))
        self.root.ids.screen_manager.add_widget(Tela1(name="tela1"))
        self.root.ids.screen_manager.add_widget(Tela2(name="tela2"))
        self.clock_player_list()

    def clock_player_list(self):
        Clock.schedule_once(self.update_roblox_online_account_liste)
        self.scheduled_actions["update_player_list"] = Clock.schedule_interval(
            self.update_roblox_online_account_liste, self.update_time_input
        )

    def update_roblox_online_account_liste(self, *args):
        self.root.ids.liste.clear_widgets()
        self.root.ids.screen_manager.screens[1].ids.list_to_delete.clear_widgets()
        items_to_draw = RobloxAccounts.roblox_accounts_zum_checken.copy()
        if any(list(items_to_draw.keys())):
            try:
                for account in items_to_draw.keys():
                    color_text_color = self.accountcolor_offline
                    color_secondary_text_color = self.accountcolor_offline_secondary
                    secondary_text = self.account_offline_text
                    if items_to_draw[account]["online"]:
                        color_text_color = self.accountcolor_online
                        color_secondary_text_color = self.accountcolor_online_secondary
                        secondary_text = self.account_online_text
                    self.root.ids.liste.add_widget(
                        ThreeLineListItem(
                            text=account,
                            secondary_text=secondary_text,
                            text_color=color_text_color,
                            theme_text_color="Custom",
                            secondary_theme_text_color="Custom",
                            secondary_text_color=color_secondary_text_color,
                            tertiary_text=str(items_to_draw[account]["id"]),
                            tertiary_theme_text_color="Custom",
                            tertiary_text_color=self.robloxidcolor,
                            on_release=lambda x: self.open_account_in_webbrowser(x),
                        )
                    )
                    self.root.ids.screen_manager.screens[
                        1
                    ].ids.list_to_delete.add_widget(
                        ThreeLineListItem(
                            text=account,
                            secondary_text="Click here to delete this account",
                            text_color=color_text_color,
                            theme_text_color="Custom",
                            secondary_theme_text_color="Custom",
                            secondary_text_color=color_secondary_text_color,
                            tertiary_text=str(items_to_draw[account]["id"]),
                            tertiary_theme_text_color="Custom",
                            tertiary_text_color=self.robloxidcolor,
                            on_release=lambda x: self.tap_to_delete(x),
                        )
                    )
                    if secondary_text == self.account_online_text:
                        if self.root.ids.screen_manager.current == "":
                            toast(f"{account} is online")
                        try:
                            self.threaded_toasts["toast"].kill()
                        except:
                            pass
                        self.show_toast(account)
            except Exception as Fehler:
                print_exception(Fehler)

    def tap_to_delete(self, instance):
        account = instance.text
        cprint.red(f"deleting {account}")
        del RobloxAccounts.roblox_accounts_zum_checken[account]
        self.update_roblox_online_account_liste()
        RobloxAccounts.write_accounts_to_search_for()

    def open_account_in_webbrowser(self, instance):
        account = instance.tertiary_text
        if str(account).isnumeric():
            webbrowser.open(fr"""https://web.roblox.com/users/{account}/profile""")

    def add_new_player(self, account):
        # self.scheduled_actions['update_player_list'].cancel()
        self.root.ids.screen_manager.screens[1].ids.textbox_new_player.text = ""
        cprint.cyan(f"New player added: {account}")
        with open(accountfile, mode="a", encoding="utf-8") as f:
            f.write(f"\n{account}")
        RobloxAccounts.read_roblox_accounts_to_search_for()

    def on_request_close(self, *args):
        global app_is_closed
        app_is_closed = True
        try:
            t.kill()
        except:
            pass
        try:
            self.threaded_toasts["toast"].kill()
        except:
            pass


if __name__ == "__main__":
    FileConfig = ConfigReader()
    RobloxAccounts = RobloxChecker()
    t = kthread.KThread(
        target=RobloxAccounts.constant_update, name="roblox_constant_update"
    )
    t.start()
    TestNavigationDrawer().run()
    sys.exit()
