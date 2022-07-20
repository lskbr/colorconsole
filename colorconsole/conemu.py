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

from cgi import print_arguments
import sys
import msvcrt
from ctypes import windll, byref
from .ansi_codes import ESCAPE, CODES, COLORS_FG, COLORS_BK
from .win_common import (
    GetConsoleScreenBufferInfo,
    CONSOLE_SCREEN_BUFFER_INFO,
    SetConsoleCP,
    SetConsoleOutputCP,
    WriteConsoleA,
    c_char_p,
    DWORD,
    CP_UTF8,
)


class Terminal:
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    WAIT_TIMEOUT = 0x00000102
    WAIT_OBJECT_0 = 0

    def __init__(self):
        self.fg = None
        self.bk = None
        self.havecolor = 1
        self.dotitles = 1
        self.stdout_handle = windll.kernel32.GetStdHandle(Terminal.STD_OUTPUT_HANDLE)
        self.stdin_handle = windll.kernel32.GetStdHandle(Terminal.STD_INPUT_HANDLE)
        self.reset_attrib = self.__get_text_attr()
        self.savedX = 0
        self.savedY = 0
        self.type = "CONEMU"
        self.new_windows_terminal = False
        SetConsoleCP(CP_UTF8)
        SetConsoleOutputCP(CP_UTF8)
        sys.stdout.reconfigure(encoding="utf-8")

    def __get_console_info(self):
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        GetConsoleScreenBufferInfo(self.stdout_handle, byref(csbi))
        return csbi

    def __get_text_attr(self):
        return self.__get_console_info().wAttributes

    def restore_buffered_mode(self):
        pass

    def enable_unbuffered_input_mode(self):
        pass

    def putch(self, ch):
        msvcrt.putc(ch)

    def getch(self):
        return msvcrt.getch()

    def getche(self):
        return msvcrt.getche()

    def kbhit(self, timeout=0):
        return msvcrt.kbhit()

    def no_colors(self):
        self.havecolor = 0

    def set_color(self, fg=None, bk=None):
        if fg is not None:
            sys.stdout.write(ESCAPE + COLORS_FG[fg])
        if bk is not None:
            sys.stdout.write(ESCAPE + COLORS_BK[bk])

    def set_title(self, title):
        sys.stderr.write("\x1b]1;\x07\x1b]2;" + str(title) + "\x07")
        sys.stderr.flush()

    def cprint(self, fg, bk, text):
        self.set_color(fg, bk)
        self.print(text)

    def print(self, text):
        if type(text) is not str:
            text = str(text)
        w = DWORD(0)
        x_utf_8 = text.encode("UTF-8")
        x_len = len(x_utf_8)
        WriteConsoleA(self.stdout_handle, c_char_p(x_utf_8), x_len, byref(w), None)

    def print_at(self, x, y, text):
        self.gotoXY(x, y)
        self.print(text)

    def output_code(self, code):
        sys.stdout.write(code)
        sys.stdout.flush()

    def clear(self):
        self.output_code(CODES["clear"])

    def gotoXY(self, x, y):
        self.output_code(CODES["gotoxy"] % (y, x))

    def save_pos(self):
        self.output_code(CODES["save"])

    def restore_pos(self):
        self.output_code(CODES["restore"])

    def reset(self):
        self.output_code(CODES["reset"])

    def move_left(self, c=1):
        self.output_code(CODES["move_left"] % c)

    def move_right(self, c=1):
        self.output_code(CODES["move_right"] % c)

    def move_up(self, c=1):
        self.output_code(CODES["move_up"] % c)

    def move_down(self, c=1):
        self.output_code(CODES["move_down"] % c)

    def columns(self):
        csbi = self.__get_console_info()
        return csbi.dwSize.X

    def lines(self):
        csbi = self.__get_console_info()
        return csbi.dwSize.Y

    def underline(self):
        self.output_code(CODES["underline"])

    def underline_off(self):
        self.output_code(CODES["underline_off"])

    def blink(self):
        self.output_code(CODES["blink"])

    def blink_off(self):
        self.output_code(CODES["blink_off"])

    def reverse(self):
        self.output_code(CODES["reverse"])

    def reverse_off(self):
        self.output_code(CODES["reverse_off"])

    def italic(self):
        self.output_code(CODES["italic"])

    def italic_off(self):
        self.output_code(CODES["italic_off"])

    def crossed(self):
        self.output_code(CODES["crossed"])

    def crossed_off(self):
        self.output_code(CODES["crossed_off"])

    def invisible(self):
        self.output_code(CODES["invisible"])

    def reset_colors(self):
        self.default_background()
        self.default_foreground
        self.reset()

    def xterm256_set_fg_color(self, color):
        self.output_code(ESCAPE + "38;5;%dm" % color)

    def xterm24bit_set_fg_color(self, r, g, b):
        self.output_code(ESCAPE + "38;2;%d;%d;%dm" % (r, g, b))

    def xterm256_set_bk_color(self, color):
        self.output_code(ESCAPE + "48;5;%dm" % color)

    def xterm24bit_set_bk_color(self, r, g, b):
        self.output_code(ESCAPE + "48;2;%d;%d;%dm" % (r, g, b))

    def default_foreground(self):
        self.output_code(ESCAPE + "39m")

    def default_background(self):
        self.output_code(ESCAPE + "49m")

    def hide_cursor(self):
        self.output_code(ESCAPE + "?25l")

    def show_cursor(self):
        self.output_code(ESCAPE + "?2h")

    def enable_window_events(self):
        pass

    def disable_windows_events(self):
        pass
