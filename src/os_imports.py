from kivy.utils import platform  # android, ios, win, macosx, linux, unknown
from apple_notifications import *
from exception_handler import print_exception
def sendmessage(message):
    subprocess.Popen(["notify-send", message])
    return
class ToastNotifier:
    def show_toast(self, **kwargs):
        pass
class vibrator:
    def vibrator(self, **kwargs):
        pass

if platform == "win":
    try:
        from win10toast import ToastNotifier
    except Exception as Fehler:
        print_exception(Fehler)
if platform == "ios" or platform == "android":
    try:
        from plyer import vibrator
    except Exception as Fehler:
        print_exception(Fehler)
