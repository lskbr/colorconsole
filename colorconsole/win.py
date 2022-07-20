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
# Thanks to:
#            Sylvain MOUQUET (https://github.com/sylvainmouquet)
#            for set_title bug fixing and enhancements
#
#

import sys
import os
import msvcrt
import threading

from ctypes import byref, wintypes

from .ansi_codes import ESCAPE, CODES
from .win_common import (
    SetConsoleTextAttribute,
    GetConsoleScreenBufferInfo,
    SetConsoleTitle,
    SetConsoleCursorPosition,
    FillConsoleOutputCharacter,
    FillConsoleOutputAttribute,
    WriteConsoleA,
    GetStdHandle,
    SetConsoleCP,
    SetConsoleOutputCP,
    SetConsoleCursorInfo,
    GetConsoleCursorInfo,
    ReadConsoleInputW,
    SetConsoleScreenBufferSize,
    CONSOLE_SCREEN_BUFFER_INFO,
    CONSOLE_CURSOR_INFO,
    DWORD,
    COORD,
    CP_UTF8,
    c_char_p,
    c_wchar_p,
    GetConsoleMode,
    SetConsoleMode,
    wait_for_handles,
    ENABLE_VIRTUAL_TERMINAL_PROCESSING,
    ENABLE_WINDOW_INPUT,
    WINDOW_BUFFER_SIZE_EVENT,
    INPUT_RECORD,
)

from .win_pallet import WT_COLORS_256


class EventReader(threading.Thread):
    def __init__(self, stdin_handle, target):
        super().__init__(daemon=False)
        self.stdin_handle = stdin_handle
        self._stop_event = threading.Event()
        self.target = target

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        read_count = wintypes.DWORD(0)
        MAX_EVENTS = 1024
        arrtype = INPUT_RECORD * MAX_EVENTS
        input_records = arrtype()
        while not self.stopped():
            ret = wait_for_handles([self.stdin_handle], 200)
            if ret is None:
                continue

            ReadConsoleInputW(
                self.stdin_handle, byref(input_records), MAX_EVENTS, byref(read_count)
            )
            # print(f"Events read: {read_count.value}")
            read_input_records = input_records[: read_count.value]
            for input_record in read_input_records:
                event_type = input_record.EventType
                # print(f"{event_type}")
                if event_type == WINDOW_BUFFER_SIZE_EVENT:
                    # Window size changed, store size
                    size = input_record.Event.WindowBufferSizeEvent.dwSize
                    new_size = (size.X, size.Y)
                    if self.target.on_resize:
                        self.target.on_resize(*new_size)


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
        self.stdout_handle = GetStdHandle(Terminal.STD_OUTPUT_HANDLE)
        self.stdin_handle = GetStdHandle(Terminal.STD_INPUT_HANDLE)
        self.reset_attrib = self.__get_text_attr()
        self.savedX = 0
        self.savedY = 0
        self.type = "WIN"
        self.new_windows_terminal = os.getenv("WT_SESSION") is not None or False
        SetConsoleCP(CP_UTF8)
        SetConsoleOutputCP(CP_UTF8)
        self.event_reader = None
        self.on_resize = None
        sys.stdout.reconfigure(encoding="utf-8")
        if self.new_windows_terminal:
            self.enable_virtual_terminal_processing()

    def enable_window_events(self):
        if self.new_windows_terminal:
            z = DWORD()
            GetConsoleMode(self.stdin_handle, byref(z))
            z = DWORD(z.value | ENABLE_WINDOW_INPUT)
            SetConsoleMode(self.stdin_handle, z)
            self.event_reader = EventReader(self.stdin_handle, self)
            self.event_reader.start()

    def enable_virtual_terminal_processing(self):
        z = DWORD()
        GetConsoleMode(self.stdout_handle, byref(z))
        z = DWORD(z.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
        SetConsoleMode(self.stdout_handle, z)

    def disable_windows_events(self):
        if self.event_reader:
            self.event_reader.stop()
            self.event_reader = None

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

    def kbhit(self, timeout=0):  # Ignores timeout...
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
        ctitle = c_wchar_p(title)
        SetConsoleTitle(ctitle)

    def cprint(self, fg, bk, text):
        self.set_color(fg, bk)
        self.win_print(text)

    def print_at(self, x, y, text):
        self.gotoXY(x, y)
        self.win_print(text)

    def print(self, text):
        self.win_print(text)

    def clear(self):  # From kb q99261
        if self.new_windows_terminal:
            self.output_code(CODES["clear"])
        else:
            rp = COORD()
            wr = DWORD()
            csbi = CONSOLE_SCREEN_BUFFER_INFO()
            GetConsoleScreenBufferInfo(self.stdout_handle, byref(csbi))
            sx = csbi.dwSize.X * csbi.dwSize.Y

            FillConsoleOutputCharacter(self.stdout_handle, 32, sx, rp, byref(wr))
            FillConsoleOutputAttribute(
                self.stdout_handle, csbi.wAttributes, sx, rp, byref(wr)
            )

    def gotoXY(self, x, y):
        p = COORD()
        p.X = int(x)
        p.Y = int(y)
        SetConsoleCursorPosition(self.stdout_handle, p)

    def save_pos(self):
        csbi = self.__get_console_info()
        self.savedX = csbi.dwCursorPosition.X
        self.savedY = csbi.dwCursorPosition.Y

    def restore_pos(self):
        self.gotoXY(self.savedX, self.savedY)

    def reset(self):
        self.__set_text_attr(self.reset_attrib)

    def __move_from(self, dx, dy):
        csbi = self.__get_console_info()
        ax = csbi.dwCursorPosition.X
        ay = csbi.dwCursorPosition.Y
        self.gotoXY(ax + dx, ay + dy)

    def move_left(self, c=1):
        self.__move_from(-c, 0)

    def move_right(self, c=1):
        self.__move_from(c, 0)

    def move_up(self, c=1):
        self.__move_from(0, -c)

    def move_down(self, c=1):
        self.__move_from(0, c)

    def set_console_size(self, columns, lines):
        coord = COORD()
        coord.X = columns
        coord.Y = lines
        SetConsoleScreenBufferSize(self.stdout_handle, byref(coord))

    def columns(self):
        csbi = self.__get_console_info()
        return csbi.dwSize.X

    def lines(self):
        csbi = self.__get_console_info()
        return csbi.dwSize.Y

    def output_code(self, code):
        if self.new_windows_terminal:
            sys.stdout.write(code)
            sys.stdout.flush()

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
        self.reset()

    def win_print(self, x):
        # https://github.com/microsoft/terminal/issues/10055
        if type(x) is not str:
            x = str(x)
        w = DWORD(0)
        x_utf_8 = x.encode("UTF-8")
        x_len = len(x_utf_8)
        WriteConsoleA(self.stdout_handle, c_char_p(x_utf_8), x_len, byref(w), None)

    def xterm256_set_fg_color(self, color):
        if self.new_windows_terminal:
            rgb = WT_COLORS_256[color]
            sys.stdout.write(ESCAPE + f"38;2;{rgb}m")
            sys.stdout.flush()

    def xterm256_set_bk_color(self, color):
        rgb = WT_COLORS_256[color]
        self.output_code(ESCAPE + f"48;2;{rgb}m")

    def xterm24bit_set_fg_color(self, r, g, b):
        self.output_code(ESCAPE + "38;2;%d;%d;%dm" % (r, g, b))

    def xterm24bit_set_bk_color(self, r, g, b):
        self.output_code(ESCAPE + "48;2;%d;%d;%dm" % (r, g, b))

    def default_foreground(self):
        self.output_code(ESCAPE + "39m")

    def default_background(self):
        self.output_code(ESCAPE + "49m")

    def hide_cursor(self):
        cinfo = CONSOLE_CURSOR_INFO()
        GetConsoleCursorInfo(self.stdout_handle, byref(cinfo))
        cinfo.bVisible = False
        SetConsoleCursorInfo(self.stdout_handle, byref(cinfo))

    def show_cursor(self):
        cinfo = CONSOLE_CURSOR_INFO()
        GetConsoleCursorInfo(self.stdout_handle, byref(cinfo))
        cinfo.bVisible = True
        SetConsoleCursorInfo(self.stdout_handle, byref(cinfo))
