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

from .ansi_codes import ESCAPE, CODES, COLORS_FG, COLORS_BK
from .win_common import (
    SetConsoleTextAttribute,
    GetConsoleScreenBufferInfo,
    SetConsoleTitle,
    SetConsoleCursorPosition,
    FillConsoleOutputCharacter,
    FillConsoleOutputAttribute,
    WaitForSingleObject,
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
    WAIT_OBJECT_0,
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
        self._stdout_handle = GetStdHandle(Terminal.STD_OUTPUT_HANDLE)
        self._stdin_handle = GetStdHandle(Terminal.STD_INPUT_HANDLE)
        self.reset_attrib = self.__get_text_attr()
        self._savedX = 0
        self._savedY = 0
        self.__detect_terminal_type()
        SetConsoleCP(CP_UTF8)
        SetConsoleOutputCP(CP_UTF8)
        self.__event_reader = None
        self.on_resize = None
        sys.stdout.reconfigure(encoding="utf-8")
        if self.new_windows_terminal:
            self.enable_virtual_terminal_processing()

    def __detect_terminal_type(self):
        """Check for env variables to detect:
        the old windows console, new windows terminal or conemu."""
        self.conemu = os.getenv("ConEmuPid") is not None
        self.type = "WIN" if not self.conemu else "CONEMU"
        self.new_windows_terminal = os.getenv("WT_SESSION") is not None or False
        self.ansi_commands = self.new_windows_terminal or self.conemu
        self.ansi_256colors = self.new_windows_terminal or self.conemu
        self.ansi_24bit_colors = self.new_windows_terminal or self.conemu

    def enable_window_events(self):
        if self.new_windows_terminal:
            z = DWORD()
            GetConsoleMode(self._stdin_handle, byref(z))
            z = DWORD(z.value | ENABLE_WINDOW_INPUT)
            SetConsoleMode(self._stdin_handle, z)
            self.__event_reader = EventReader(self._stdin_handle, self)
            self.__event_reader.start()

    def enable_virtual_terminal_processing(self):
        if self.new_windows_terminal:
            z = DWORD()
            GetConsoleMode(self._stdout_handle, byref(z))
            z = DWORD(z.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
            SetConsoleMode(self._stdout_handle, z)

    def disable_windows_events(self):
        if self.__event_reader:
            self.__event_reader.stop()
            self.__event_reader = None

    def restore_buffered_mode(self):
        """Restore buffered mode (line oriented)."""
        pass

    def enable_unbuffered_input_mode(self):
        """Enable unbuffered mode (character oriented)."""
        pass

    def putch(self, ch):
        """Print a single character to stdout"""
        msvcrt.putc(ch)

    def getch(self) -> str:
        """Read next key"""
        return msvcrt.getch().decode("utf-8")

    def getche(self) -> str:
        """Read next key and print it on screen (echo)"""
        return msvcrt.getche().decode("utf-8")

    def kbhit(self, timeout: float = 0) -> bool:
        """Pauses the program until timeout (in seconds) or a key is available in stdin.
        Returns True if a key is available, False if the timeout was reached with no input"""
        # Convert timeout to milisseconds
        mtimeout = int(timeout * 1000)
        wr = WaitForSingleObject(self._stdin_handle, mtimeout)
        return wr == WAIT_OBJECT_0
        # return msvcrt.kbhit()

    def no_colors(self) -> None:
        """Turn off color display. All further color changing methods will produce no effect."""
        self.havecolor = 0

    def set_color(self, fg: int = None, bk: int = None) -> None:
        """Sets the foregound and background colors. This method only supports 16 color consoles.
        fg and bg must be between 0 and 15."""
        if self.type == "WIN":
            actual = self.__get_text_attr()
            if fg is None:
                fg = actual & 0x000F
            if bk is None:
                bk = actual & 0x00F0
            else:
                bk <<= 4
            self.__set_text_attr(fg + bk)
        else:
            if fg is not None:
                sys.stdout.write(ESCAPE + COLORS_FG[fg])
            if bk is not None:
                sys.stdout.write(ESCAPE + COLORS_BK[bk])

    def __get_console_info(self):
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        GetConsoleScreenBufferInfo(self._stdout_handle, byref(csbi))
        return csbi

    def __get_text_attr(self):
        return self.__get_console_info().wAttributes

    def __set_text_attr(self, color):
        sys.stdout.flush()
        SetConsoleTextAttribute(self._stdout_handle, color)

    def set_title(self, title: str) -> None:
        """Change the title of the terminal windows to title."""
        ctitle = c_wchar_p(title)
        SetConsoleTitle(ctitle)

    def cprint(self, fg: int, bk: int, text: str) -> None:
        """Combine color change and print in a single method call."""
        self.set_color(fg, bk)
        self.__win_print(text)

    def print_at(self, x: int, y: int, text: str) -> None:
        """Print the text at the specified column (x) and line (y)."""
        self.gotoXY(x, y)
        self.__win_print(text)

    def print(self, text: str) -> None:
        """Print the text on screen."""
        self.__win_print(text)

    def clear(self) -> None:  # From kb q99261
        """Clear the screen."""
        if self.ansi_commands:
            self.output_code(CODES["clear"])
        else:
            rp = COORD()
            wr = DWORD()
            csbi = CONSOLE_SCREEN_BUFFER_INFO()
            GetConsoleScreenBufferInfo(self._stdout_handle, byref(csbi))
            sx = csbi.dwSize.X * csbi.dwSize.Y

            FillConsoleOutputCharacter(self._stdout_handle, 32, sx, rp, byref(wr))
            FillConsoleOutputAttribute(
                self._stdout_handle, csbi.wAttributes, sx, rp, byref(wr)
            )

    def gotoXY(self, x: int, y: int) -> None:
        """Move the cursor to column (x), line (y)."""
        p = COORD()
        p.X = int(x)
        p.Y = int(y)
        SetConsoleCursorPosition(self._stdout_handle, p)

    def save_pos(self) -> None:
        """Save the current cursor position."""
        if self.ansi_commands:
            self.output_code(CODES["save"])
        else:
            csbi = self.__get_console_info()
            self._savedX = csbi.dwCursorPosition.X
            self._savedY = csbi.dwCursorPosition.Y

    def restore_pos(self) -> None:
        """Restore the cursor position to the previously saved one."""
        if self.ansi_commands:
            self.output_code(CODES["restore"])
        else:
            self.gotoXY(self._savedX, self._savedY)

    def reset(self) -> None:
        """Reset terminal colors and settings to the default ones."""
        if self.ansi_commands:
            self.output_code(CODES["reset"])
        else:
            self.__set_text_attr(self.reset_attrib)

    def __move_from(self, dx, dy):
        csbi = self.__get_console_info()
        ax = csbi.dwCursorPosition.X
        ay = csbi.dwCursorPosition.Y
        self.gotoXY(ax + dx, ay + dy)

    def move_left(self, c: int = 1) -> None:
        """Move the cursor to the left (c or 1) columns"""
        self.__move_from(-c, 0)

    def move_right(self, c: int = 1):
        """Move the cursor to the right (c or 1) columns"""
        self.__move_from(c, 0)

    def move_up(self, c: int = 1):
        """Move the cursor one line up (c or 1) lines"""
        self.__move_from(0, -c)

    def move_down(self, c: int = 1):
        """Move the cursor one line down (c or 1) lines"""
        self.__move_from(0, c)

    def set_console_size(self, columns: int, lines: int):
        coord = COORD()
        coord.X = columns
        coord.Y = lines
        SetConsoleScreenBufferSize(self._stdout_handle, byref(coord))

    def columns(self) -> int:
        """Get the number of columns available on screen."""
        csbi = self.__get_console_info()
        return csbi.dwSize.X

    def lines(self) -> int:
        """Get the number of lines available on screen."""
        csbi = self.__get_console_info()
        return csbi.dwSize.Y

    def output_code(self, code):
        """Output a code sequence to the stdout, flushing it just after."""
        if self.ansi_commands:
            sys.stdout.write(code)
            sys.stdout.flush()

    def underline(self) -> None:
        """Turn font underline on."""
        self.output_code(CODES["underline"])

    def underline_off(self) -> None:
        """Turn font underline off."""
        self.output_code(CODES["underline_off"])

    def blink(self) -> None:
        """Make foreground and background color to blink."""
        self.output_code(CODES["blink"])

    def blink_off(self):
        """Turn blink off."""
        self.output_code(CODES["blink_off"])

    def reverse(self) -> None:
        """Swap background and foreground colors"""
        self.output_code(CODES["reverse"])

    def reverse_off(self) -> None:
        """Turn reverse mode off"""
        self.output_code(CODES["reverse_off"])

    def italic(self) -> None:
        """Turn font italic on"""
        self.output_code(CODES["italic"])

    def italic_off(self) -> None:
        """Turn font italic off"""
        self.output_code(CODES["italic_off"])

    def crossed(self) -> None:
        """Turn crossed text on"""
        self.output_code(CODES["crossed"])

    def crossed_off(self) -> None:
        """Turn crossed text off"""
        self.output_code(CODES["crossed_off"])

    def invisible(self) -> None:
        """Make text invisible"""
        self.output_code(CODES["invisible"])

    def reset_colors(self) -> None:
        """Reset the background and foreground color to the default ones.
        Reset terminal attributes to normal."""
        self.reset()

    def __win_print(self, x):
        # https://github.com/microsoft/terminal/issues/10055
        if type(x) is not str:
            x = str(x)
        w = DWORD(0)
        x_utf_8 = x.encode("UTF-8")
        x_len = len(x_utf_8)
        WriteConsoleA(self._stdout_handle, c_char_p(x_utf_8), x_len, byref(w), None)

    def xterm256_set_fg_color(self, color: int):
        """Set the foreground color using a 256 colors pallete"""
        if self.ansi_256colors:
            rgb = WT_COLORS_256[color]
            sys.stdout.write(ESCAPE + f"38;2;{rgb}m")
            sys.stdout.flush()

    def xterm256_set_bk_color(self, color: int):
        """Set the background color using a 256 colors pallete"""
        if self.ansi_256colors:
            rgb = WT_COLORS_256[color]
            self.output_code(ESCAPE + f"48;2;{rgb}m")

    def xterm24bit_set_fg_color(self, r: int, g: int, b: int):
        """Set the foreground color using the red (r), green (g) and blue (b) values passed to it.
        r, g and b must be between 0 and 255."""
        if self.ansi_24bit_colors:
            self.output_code(ESCAPE + "38;2;%d;%d;%dm" % (r, g, b))

    def xterm24bit_set_bk_color(self, r: int, g: int, b: int) -> None:
        """Set the background color using the red (r), green (g) and blue (b) values passed to it.
        r, g and b must be between 0 and 255."""
        if self.ansi_24bit_colors:
            self.output_code(ESCAPE + "48;2;%d;%d;%dm" % (r, g, b))

    def default_foreground(self) -> None:
        """Reset the foreground color to the terminal's default one."""
        self.output_code(ESCAPE + "39m")

    def default_background(self) -> None:
        """Reset the background color to the terminal's default one."""
        self.output_code(ESCAPE + "49m")

    def hide_cursor(self) -> None:
        """Hides the cursor on screen"""
        if self.ansi_commands:
            self.output_code(ESCAPE + "?25l")
        else:
            cinfo = CONSOLE_CURSOR_INFO()
            GetConsoleCursorInfo(self._stdout_handle, byref(cinfo))
            cinfo.bVisible = False
            SetConsoleCursorInfo(self._stdout_handle, byref(cinfo))

    def show_cursor(self) -> None:
        """Make the cursor visible on screen"""
        if self.ansi_commands:
            self.output_code(ESCAPE + "?2h")
        else:
            cinfo = CONSOLE_CURSOR_INFO()
            GetConsoleCursorInfo(self._stdout_handle, byref(cinfo))
            cinfo.bVisible = True
            SetConsoleCursorInfo(self._stdout_handle, byref(cinfo))
