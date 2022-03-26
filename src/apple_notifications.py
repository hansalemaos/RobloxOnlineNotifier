import subprocess
from typing import List, Union


def quotify(string):
    return f'"{string}"'


def run_command(command: Union[str, List]):
    result = subprocess.check_output(command)
    return result.decode("utf-8")


def run_applescript(script: str, no_return: bool = False):
    command = ["osascript", "-e"]
    if no_return:
        command.append(script)
    else:
        command.append(f"set answer to {script}\nreturn answer")
    return run_command(command)


class ApplescriptNotification:
    def __init__(self, text: Union[str, None] = None) -> None:

        self.applescript = "display notification "
        if text is not None:
            self.applescript += f"{quotify(text)} "

    def with_title(self, title):
        if title is not None:
            self.applescript += f"with title {quotify(title)} "

        return self

    def with_subtitle(self, subtitle: Union[str, None]):
        if subtitle is not None:
            self.applescript += f"subtitle {quotify(subtitle)} "

        return self

    def send(self):
        return run_applescript(self.applescript, no_return=True)


# ApplescriptNotification("Text").with_title("Title").with_subtitle("Subtitle").send()
