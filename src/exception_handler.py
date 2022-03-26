import sys
import os
import traceback
from time import strftime
from cprint import cprint

print_exception = lambda x: exception_handler(sys.exc_info(), strftime("%Y_%m_%d_%H_%M_%S"), x, print_globals=True)
def exception_handler(e11, e13, e4, print_globals=True):
    '''
    use like
    try:
        print(5/0)
    except Exception as e3:
        print_exception(e3)
    '''
    def get_traceback(e):
        lines = traceback.format_exception(type(e), e, e.__traceback__)
        return cprint.yellow(''.join(lines), False)
    exc_type, exc_obj, exc_tb = e11
    try:
        print('----------------------EXCEPTION START ----------------------------------------------------------')
        print('TIME OF EXCEPTION: ' + cprint.red(e13, False)+' \n', False)
        tmp_global = globals().copy()
        meldung = [f'{variablenname}'.ljust(100) + str(wert).strip()[:200] for variablenname,wert in tmp_global.items()]
        if print_globals:
            print('           ------------------------GLOBALS START------------------------')
            for ini,mel in enumerate(meldung):
                if ini%2 ==0:
                    cprint.yellow(mel)
                elif ini%2 !=0:
                    cprint.red(mel)
            print('           ------------------------GLOBALS END------------------------')
        print(cprint.magenta(f'Error in file:'.ljust(100), False) + cprint.red(str(os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]), False))
        print(cprint.blue(f'Error in line:'.ljust(100), False) + cprint.magenta(str(exc_tb.tb_lineno), False))
        print(cprint.cyan(f'Type of error:'.ljust(100), False)  + cprint.white(str(e4), False))
        cprint.red('--------------TRACEBACK START--------------')
        print(get_traceback(e4))
        cprint.red('--------------TRACEBACK END--------------')

    except Exception as Fehler:
        print(Fehler)


