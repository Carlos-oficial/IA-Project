import time

import pytermgui as ptg


def macro_time(fmt: str) -> str:
    return time.strftime(fmt)


def run():
    ptg.tim.define("!time", macro_time)
    with ptg.WindowManager() as manager:
        manager.layout.add_slot("Body")
        manager.add(
            ptg.Window(
                "[bold]Olá Jólio olha aqui as horas:[/]\n\n[!time 70]%c", box="EMPTY"
            )
        )
