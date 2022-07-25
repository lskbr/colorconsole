#!/usr/bin/env python
#
#    colorconsole
#    Copyright © 2010-2022 Nilo Menezes
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Inspired/copied/adapted from:
#
# output.py from Gentoo and
# http://code.activestate.com/recipes/572182-how-to-implement-kbhit-on-linux/ and
# http://www.burgaud.com/bring-colors-to-the-windows-console-with-python/
#

import os
import sys
from typing import Protocol

colors = {
    "BLACK": 0,
    "BLUE": 1,
    "GREEN": 2,
    "CYAN": 3,
    "RED": 4,
    "PURPLE": 5,
    "BROWN": 6,
    "LGREY": 7,
    "DGRAY": 8,
    "LBLUE": 9,
    "LGREEN": 10,
    "LCYAN": 11,
    "LRED": 12,
    "LPURPLE": 13,
    "YELLOW": 14,
    "WHITE": 15,
}

color_numbers_to_names = {v: k for k, v in colors.items()}


class TerminalProtocol(Protocol):
    def enable_virtual_terminal_processing(self):
        ...

    def restore_buffered_mode(self) -> None:
        ...

    def enable_unbuffered_input_mode(self) -> None:
        ...

    def putch(self, ch: str) -> None:
        ...

    def getch(self) -> str:
        ...

    def getche(self) -> str:
        ...

    def kbhit(self, timeout: float = 0) -> bool:
        ...

    def no_colors(self) -> None:
        ...

    def set_color(self, fg: int = None, bk: int = None) -> None:
        ...

    def set_title(self, title: str) -> None:
        ...

    def cprint(self, fg: int, bk: int, text: str) -> None:
        ...

    def print_at(self, x: int, y: int, text: str) -> None:
        ...

    def print(self, text: str) -> None:
        ...

    def clear(self) -> None:
        ...

    def gotoXY(self, x: int, y: int) -> None:
        ...

    def save_pos(self) -> None:
        ...

    def restore_pos(self) -> None:
        ...

    def reset(self) -> None:
        ...

    def move_left(self, c: int = 1) -> None:
        ...

    def move_right(self, c: int = 1):
        ...

    def move_up(self, c: int = 1):
        ...

    def move_down(self, c: int = 1):
        ...

    def columns(self) -> int:
        ...

    def lines(self) -> int:
        ...

    def underline(self):
        ...

    def underline_off(self) -> None:
        ...

    def blink(self) -> None:
        ...

    def blink_off(self) -> None:
        ...

    def reverse(self) -> None:
        ...

    def reverse_off(self) -> None:
        ...

    def italic(self) -> None:
        ...

    def italic_off(self) -> None:
        ...

    def crossed(self) -> None:
        ...

    def crossed_off(self) -> None:
        ...

    def invisible(self) -> None:
        ...

    def reset_colors(self) -> None:
        ...

    def xterm256_set_fg_color(self, color: int):
        ...

    def xterm256_set_bk_color(self, color: int):
        ...

    def xterm24bit_set_fg_color(self, r: int, g: int, b: int):
        ...

    def xterm24bit_set_bk_color(self, r: int, g: int, b: int) -> None:
        ...

    def default_foreground(self) -> None:
        ...

    def default_background(self) -> None:
        ...

    def hide_cursor(self) -> None:
        ...

    def show_cursor(self) -> None:
        ...

    def enable_window_events(self) -> None:
        ...

    def disable_windows_events(self) -> None:
        ...


def make_ansi() -> TerminalProtocol:
    import colorconsole.ansi

    return colorconsole.ansi.Terminal()


def make_conemu() -> TerminalProtocol:
    import colorconsole.conemu

    return colorconsole.conemu.Terminal()


def make_winconsole() -> TerminalProtocol:
    import colorconsole.win

    return colorconsole.win.Terminal()


def is_conemu() -> bool:
    return False if os.getenv("ConEmuPid") is None else True


def get_terminal(conEmu=False) -> TerminalProtocol:
    if os.name == "posix":
        return make_ansi()
    elif os.name == "nt":
        if conEmu:
            return make_conemu()
        else:
            return make_winconsole()
    else:
        raise RuntimeError("Unknown or unsupported terminal")
