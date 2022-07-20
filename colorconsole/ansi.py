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
        self.get_terminal_size()
        self.on_resize = None
        self.install_resize_trigger()

    def resize_handler(self, signum, frame):
        self.get_terminal_size()
        if self.on_resize:
            self.on_resize(self.ncolumns, self.nlines)

    def install_resize_trigger(self):
        signal.signal(signal.SIGWINCH, self.resize_handler)

    def restore_buffered_mode(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def enable_unbuffered_input_mode(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

    def putch(self, ch):
        sys.stdout.write(ch)

    def getch(self):
        return sys.stdin.read(1)

    def getche(self):
        ch = self.getch()
        self.putch(ch)
        return ch

    def kbhit(self, timeout=0):
        dr, dw, de = select([sys.stdin], [], [], timeout)
        return dr != []

    def no_colors(self):
        self.havecolor = 0

    def set_color(self, fg=None, bk=None):
        if fg is not None:
            sys.stdout.write(ESCAPE + COLORS_FG[fg])
        if bk is not None:
            sys.stdout.write(ESCAPE + COLORS_BK[bk])

    def set_title(self, title):
        if self.type in [
            "xterm",
            "Eterm",
            "aterm",
            "rxvt",
            "xterm-color",
            "xterm-256color",
        ]:
            self.output_code("\x1b]1;\x07\x1b]2;" + str(title) + "\x07")

    def cprint(self, fg, bk, text):
        self.set_color(fg, bk)
        self.print(text)

    def print_at(self, x, y, text):
        self.gotoXY(x, y)
        self.print(text)

    def print(self, text):
        print(text, end="")
        sys.stdout.flush()

    def output_code(self, code):
        sys.stdout.write(code)
        sys.stdout.flush()

    def clear(self):
        self.output_code(CODES["clear"])

    def gotoXY(self, x, y):
        x += 1
        y += 1
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

    def get_terminal_size(self):
        s = struct.pack("HHHH", 0, 0, 0, 0)
        t = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
        self.nlines, self.ncolumns = struct.unpack("HHHH", t)[0:2]

    def columns(self):
        self.get_terminal_size()
        return self.ncolumns

    def lines(self):
        self.get_terminal_size()
        return self.nlines

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
        sys.stdout.write(ESCAPE + "?2h")

    def enable_window_events(self):
        pass

    def disable_windows_events(self):
        pass
