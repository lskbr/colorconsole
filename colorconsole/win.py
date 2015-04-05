#!/usr/bin/env python
#
#    colorconsole
#    Copyright (C) 2010-2015 Nilo Menezes
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
# Thanks to:
#            Sylvain MOUQUET (https://github.com/sylvainmouquet)
#            for set_title bug fixing and enhancements
#
#
# Added for Python 2.6 compatibility
from __future__ import print_function
import sys
import msvcrt
from ctypes import windll, Structure, c_short, c_ushort, byref, c_uint, c_wchar_p

SHORT = c_short
WORD = c_ushort
DWORD = c_uint


class COORD(Structure):
    """struct in wincon.h."""

    _fields_ = [
                 ("X", SHORT),
                 ("Y", SHORT)
                ]


class SMALL_RECT(Structure):
    """struct in wincon.h."""

    _fields_ = [
                ("Left", SHORT),
                ("Top", SHORT),
                ("Right", SHORT),
                ("Bottom", SHORT)
                ]


class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    """struct in wincon.h."""

    _fields_ = [
                ("dwSize", COORD),
                ("dwCursorPosition", COORD),
                ("wAttributes", WORD),
                ("srWindow", SMALL_RECT),
                ("dwMaximumWindowSize", COORD)
                ]


SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo
# Added for compatibility between python 2 and 3
SetConsoleTitle = windll.kernel32.SetConsoleTitleW
cstring_p = c_wchar_p
GetConsoleTitle = windll.kernel32.GetConsoleTitleW
SetConsoleCursorPosition = windll.kernel32.SetConsoleCursorPosition
FillConsoleOutputCharacter = windll.kernel32.FillConsoleOutputCharacterA
FillConsoleOutputAttribute = windll.kernel32.FillConsoleOutputAttribute
WriteConsoleW = windll.kernel32.WriteConsoleW


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
        self.type = "WIN"

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

    def kbhit(self, timeout=0):  # Ignores timeout... should be slown down
        return msvcrt.kbhit()

    def no_colors(self):
        self.havecolor = 0

    def set_color(self, fg=None, bk=None):
        actual = self.__get_text_attr()
        if fg is None:
            fg = actual & 0x000F
        if bk is None:
            bk = actual & 0x00F0
        else:
            bk <<= 4

        self.__set_text_attr(fg + bk)

    def __get_console_info(self):
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        GetConsoleScreenBufferInfo(self.stdout_handle, byref(csbi))
        return csbi

    def __get_text_attr(self):
        return self.__get_console_info().wAttributes

    def __set_text_attr(self, color):
        sys.stdout.flush()
        SetConsoleTextAttribute(self.stdout_handle, color)

    def set_title(self, title):
        ctitle = cstring_p(title)
        SetConsoleTitle(ctitle)

    def cprint(self, fg, bk, text):
        self.set_color(fg, bk)
        self.win_print(text)

    def print_at(self, x, y, text):
            self.gotoXY(x, y)
            self.win_print(text)

    def clear(self):  # From kb q99261
        rp = COORD()
        wr = DWORD()
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        GetConsoleScreenBufferInfo(self.stdout_handle, byref(csbi))
        sx = csbi.dwSize.X * csbi.dwSize.Y

        FillConsoleOutputCharacter(self.stdout_handle, 32,
                                   sx, rp, byref(wr))
        FillConsoleOutputAttribute(self.stdout_handle, csbi.wAttributes,
                                   sx, rp, byref(wr))

    def gotoXY(self, x, y):
        p = COORD()
        p.X = int(x)
        p.Y = int(y)
        SetConsoleCursorPosition(self.stdout_handle, p)
        pass

    def save_pos(self):
        csbi = self.__get_console_info()
        self.savedX = csbi.dwCursorPosition.X
        self.savedY = csbi.dwCursorPosition.Y
        pass

    def restore_pos(self):
        self.gotoXY(self.savedX, self.savedY)

    def reset(self):
        self.__set_text_attr(self.reset_attrib)

    def __move_from(self, dx, dy):
        csbi = self.__get_console_info()
        ax = csbi.dwCursorPosition.X
        ay = csbi.dwCursorPosition.Y
        self.gotoXY(ax+dx, ay+dy)

    def move_left(self, c=1):
        self.__move_from(-c, 0)

    def move_right(self, c=1):
        self.__move_from(c, 0)

    def move_up(self, c=1):
        self.__move_from(0, -c)

    def move_down(self, c=1):
        self.__move_from(0, c)

    def columns(self):
        csbi = self.__get_console_info()
        return csbi.dwSize.X

    def lines(self):
        csbi = self.__get_console_info()
        return csbi.dwSize.Y

    def blink(self):
        pass

    def reverse(self):
        pass

    def invisible(self):
        pass

    def reset_colors(self):
        self.reset()

    def win_print(self, x):
        if(type(x) != str and type(x) != unicode):
            x = str(x)
        l = len(x)
        w = DWORD(0)
        WriteConsoleW(self.stdout_handle, cstring_p(x), l, byref(w), None)
