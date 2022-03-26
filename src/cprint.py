class cprint:
    '''
    Use like:
    cprint.red('Hallo')
    cprint.green('green')
    print(cprint.red('Hallo', False) + cprint.green('green', False))
    '''
    Red = '\033[91m'
    Green = '\033[92m'
    Blue = '\033[94m'
    Cyan = '\033[96m'
    White = '\033[97m'
    Yellow = '\033[93m'
    Magenta = '\033[95m'
    Grey = '\033[90m'
    Black = '\033[90m'
    Default = '\033[99m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def red(text, printtext=True):
        if printtext:
            print(cprint.Red + str(text) + cprint.ENDC + cprint.Default)
            return ''
        elif not printtext:
            return cprint.Red + str(text) + cprint.ENDC + cprint.Default
    def green(text, printtext=True):
        if printtext:
            print(cprint.Green + str(text) + cprint.ENDC + cprint.Default)
            return ''
        elif not printtext:
            return cprint.Green + str(text) + cprint.ENDC + cprint.Default
    def blue(text, printtext=True):
        if printtext:
            print(cprint.Blue + str(text) + cprint.ENDC + cprint.Default)
            return ''
        elif not printtext:
            return cprint.Blue + str(text) + cprint.ENDC + cprint.Default
    def cyan(text, printtext=True):
        if printtext:
            print(cprint.Cyan + str(text) + cprint.ENDC + cprint.Default)
            return ''
        elif not printtext:
            return cprint.Cyan + str(text) + cprint.ENDC + cprint.Default
    def white(text, printtext=True):
        if printtext:
            print(cprint.White + str(text) + cprint.ENDC + cprint.Default)
            return ''
        elif not printtext:
            return cprint.White + str(text) + cprint.ENDC + cprint.Default
    def yellow(text, printtext=True):
        if printtext:
            print(cprint.Yellow + str(text) + cprint.ENDC + cprint.Default)
            return ''
        elif not printtext:
            return cprint.Yellow + str(text) + cprint.ENDC + cprint.Default
    def magenta(text, printtext=True):
        if printtext:
            print(cprint.Magenta + str(text) + cprint.ENDC + cprint.Default)
            return ''
        elif not printtext:
            return cprint.Magenta + str(text) + cprint.ENDC + cprint.Default
    def grey(text, printtext=True):
        if printtext:
            print(cprint.Grey + str(text) + cprint.ENDC + cprint.Default)
            return ''
        elif not printtext:
            return cprint.Grey + str(text) + cprint.ENDC + cprint.Default
    def black(text, printtext=True):
        if printtext:
            print(cprint.Black + str(text) + cprint.ENDC + cprint.Default)
            return ''
        elif not printtext:
            return cprint.Black + str(text) + cprint.ENDC + cprint.Default

