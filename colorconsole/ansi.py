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
# 256 xterm color sheet in RGB converted from
# https://www.ditig.com/256-colors-cheat-sheet#list-of-colors

import os
import sys
import termios
import struct
import fcntl
import signal
from select import select
from .ansi_codes import ESCAPE, CODES, COLORS_FG, COLORS_BK
from typing import Tuple


class Terminal:
    def __init__(self):
        self.fg = None
        self.bk = None
        self.havecolor = 1
        self.dotitles = 1
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)
        self.new_term[3] = self.new_term[3] & ~termios.ICANON & ~termios.ECHO
        self.type = os.environ.get("TERM", "UNKNOWN-ANSI")
        self.new_windows_terminal = False
        self.nlines = 0
        self.ncolumns = 0
        self.__get_terminal_size()
        self.on_resize = None
        self.install_resize_trigger()

    def resize_handler(self, signum, frame) -> None:
        """Receive a SIGWINCH signal on Linux/Mac OS X to indicate the screen size changed.
        Updates local state about screen dimensions.
        Calls self.on_resize if one was set up."""
        self.__get_terminal_size()
        if self.on_resize:
            self.on_resize(self.ncolumns, self.nlines)

    def install_resize_trigger(self) -> None:
        if sys.platform != "win32":
            signal.signal(signal.SIGWINCH, self.resize_handler)

    def restore_buffered_mode(self) -> None:
        """Restore buffered mode (line oriented)."""
        if sys.platform != "win32":
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def enable_unbuffered_input_mode(self) -> None:
        """Enable unbuffered mode (character oriented)."""
        if sys.platform != "win32":
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

    def putch(self, ch: str) -> None:
        """Print a single character to stdout"""
        sys.stdout.write(ch)

    def getch(self) -> str:
        """Read next key"""
        return sys.stdin.read(1)

    def getche(self) -> str:
        """Read next key and print it on screen (echo)"""
        ch = self.getch()
        self.putch(ch)
        return ch

    def kbhit(self, timeout: float = 0) -> bool:
        """Pauses the program until timeout (in seconds) or a key is available in stdin.
        Returns True if a key is available, False if the timeout was reached with no input"""
        dr, dw, de = select([sys.stdin], [], [], timeout)
        return dr != []

    def no_colors(self) -> None:
        """Turn off color display. All further color changing methods will produce no effect."""
        self.havecolor = 0

    def set_color(self, fg: int = None, bk: int = None) -> None:
        """Sets the foregound and background colors. This method only supports 16 color consoles.
        fg and bg must be between 0 and 15."""

        if fg is not None:
            sys.stdout.write(ESCAPE + COLORS_FG[fg])
        if bk is not None:
            sys.stdout.write(ESCAPE + COLORS_BK[bk])

    def set_title(self, title: str) -> None:
        """Change the title of the terminal windows to title."""
        if self.type in [
            "xterm",
            "Eterm",
            "aterm",
            "rxvt",
            "xterm-color",
            "xterm-256color",
        ]:
            self.output_code("\x1b]1;\x07\x1b]2;" + str(title) + "\x07")

    def cprint(self, fg: int, bk: int, text: str) -> None:
        """Combine color change and print in a single method call."""
        self.set_color(fg, bk)
        self.print(text)

    def print_at(self, x: int, y: int, text: str) -> None:
        """Print the text at the specified column (x) and line (y)."""
        self.gotoXY(x, y)
        self.print(text)

    def print(self, text: str) -> None:
        """Print the text on screen."""
        print(text, end="")
        sys.stdout.flush()

    def output_code(self, code: str) -> None:
        """Output a code sequence to the stdout, flushing it just after."""
        sys.stdout.write(code)
        sys.stdout.flush()

    def clear(self) -> None:
        """Clear the screen."""
        self.output_code(CODES["clear"])

    def gotoXY(self, x: int, y: int) -> None:
        """Move the cursor to column (x), line (y)."""
        x += 1
        y += 1
        self.output_code(CODES["gotoxy"] % (y, x))

    def save_pos(self) -> None:
        """Save the current cursor position."""
        self.output_code(CODES["save"])

    def restore_pos(self) -> None:
        """Restore the cursor position to the previously saved one."""
        self.output_code(CODES["restore"])

    def reset(self) -> None:
        """Reset terminal colors and settings to the default ones."""
        self.output_code(CODES["reset"])

    def move_left(self, c: int = 1) -> None:
        """Move the cursor to the left (c or 1) columns"""
        self.output_code(CODES["move_left"] % c)

    def move_right(self, c: int = 1):
        """Move the cursor to the right (c or 1) columns"""
        self.output_code(CODES["move_right"] % c)

    def move_up(self, c: int = 1):
        """Move the cursor one line up (c or 1) lines"""
        self.output_code(CODES["move_up"] % c)

    def move_down(self, c: int = 1):
        """Move the cursor one line down (c or 1) lines"""
        self.output_code(CODES["move_down"] % c)

    def __get_terminal_size(self) -> Tuple[int, int]:
        """Get the current terminal size in lines and columns"""
        if sys.platform != "win32":
            s = struct.pack("HHHH", 0, 0, 0, 0)
            t = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
            self.nlines, self.ncolumns = struct.unpack("HHHH", t)[0:2]
            return self.ncolumns, self.nlines
        return -1, -1

    def columns(self) -> int:
        """Get the number of columns available on screen."""
        self.__get_terminal_size()
        return self.ncolumns

    def lines(self) -> int:
        """Get the number of lines available on screen."""
        self.__get_terminal_size()
        return self.nlines

    def underline(self) -> None:
        """ "Turn font underline on."""
        self.output_code(CODES["underline"])

    def underline_off(self) -> None:
        """ "Turn font underline off."""
        self.output_code(CODES["underline_off"])

    def blink(self) -> None:
        """ "Make foreground and background color to blink."""
        self.output_code(CODES["blink"])

    def blink_off(self) -> None:
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
        self.default_background()
        self.default_foreground
        self.reset()

    def xterm256_set_fg_color(self, color: int):
        """ "Set the foreground color using a 256 colors pallete"""
        self.output_code(ESCAPE + "38;5;%dm" % color)

    def xterm24bit_set_fg_color(self, r: int, g: int, b: int):
        """ "Set the foreground color using the red (r), green (g) and blue (b) values passed to it.
        r, g and b must be between 0 and 255."""
        self.output_code(ESCAPE + "38;2;%d;%d;%dm" % (r, g, b))

    def xterm256_set_bk_color(self, color: int):
        """ "Set the background color using a 256 colors pallete"""
        self.output_code(ESCAPE + "48;5;%dm" % color)

    def xterm24bit_set_bk_color(self, r: int, g: int, b: int) -> None:
        """ "Set the background color using the red (r), green (g) and blue (b) values passed to it.
        r, g and b must be between 0 and 255."""
        self.output_code(ESCAPE + "48;2;%d;%d;%dm" % (r, g, b))

    def default_foreground(self) -> None:
        """Reset the foreground color to the terminal's default one."""
        self.output_code(ESCAPE + "39m")

    def default_background(self) -> None:
        """Reset the background color to the terminal's default one."""
        self.output_code(ESCAPE + "49m")

    def hide_cursor(self) -> None:
        """Hides the cursor on screen"""
        self.output_code(ESCAPE + "?25l")

    def show_cursor(self) -> None:
        """Make the cursor visible on screen"""
        sys.stdout.write(ESCAPE + "?2h")

    def enable_window_events(self) -> None:
        pass

    def disable_windows_events(self) -> None:
        pass

    def enable_virtual_terminal_processing(self):
        pass
