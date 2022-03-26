import re
from cprint import cprint


def print_all_widget_attributes(di, prefix="self.root.ids.", write_to_file=None, console_output=True):
    if not any(list(di.keys())):
        if console_output:
            errormessage = f'      Nothing found in: {prefix.strip(".")}      '
            errormessage_hi = len(errormessage) * "-"
            print(
                cprint.red(f"{errormessage_hi}\n{errormessage}\n{errormessage_hi}", False)
            )
        return None
    for key, item in di.items():
        if console_output:
            message = f"↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ Widget: {str(key)} ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓"
            message_hi = len(message) * "-"
            print(cprint.yellow(f"{message_hi}\n{message}\n{message_hi}", False))
        try:
            for i in dir(item):

                if i != "ids":
                    if console_output:
                        print(
                            cprint.blue(prefix, False)
                            + cprint.red(key, False)
                            + cprint.yellow(".", False)
                            + cprint.green(i, False),
                            end=cprint.white("=", False),
                        )
                        exec(
                            f'if (str(item.{i}).startswith("<")): print(cprint.white(item.{i}, False))\nelif not (str(item.{i}).startswith("<")): print(cprint.yellow(item.{i}, False))'
                        )

                    if write_to_file is not None:
                        dictforexex = {}
                        dictforexex["val"] = ""
                        exec(f"dictforexex['val']=str(item.{i})")
                        with open(write_to_file, mode="a", encoding="utf-8") as f:
                            f.write(
                                prefix + key + "." + i + "=" + dictforexex["val"] + "\n"
                            )

                elif i == "ids":
                    print_all_widget_attributes(
                        item.ids,
                        prefix=re.sub(r"\.+", ".", f"{prefix}.{key}.ids."),
                        write_to_file=write_to_file, console_output=console_output
                    )

        except Exception as Fehler:
            print(Fehler)
        if key == "screen_manager":
            for ini, screen in enumerate(item.screens):
                try:
                    newprefix = re.sub(
                        r"\.+", ".", prefix + f".screen_manager.screens[{ini}].ids."
                    )
                    print_all_widget_attributes(
                        screen.ids, prefix=newprefix, write_to_file=write_to_file, console_output=console_output
                    )
                except Exception as Fehler:
                    print(Fehler)