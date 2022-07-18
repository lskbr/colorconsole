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
        self.ncolumns = 80
        self.nlines = 24
        self.type = os.environ.get("TERM", "UNKNOWN-ANSI")
        self.new_windows_terminal = False

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
        if self.type in ["xterm", "Eterm", "aterm", "rxvt", "xterm-color"]:
            sys.stderr.write("\x1b]1;\x07\x1b]2;" + str(title) + "\x07")
            sys.stderr.flush()

    def cprint(self, fg, bk, text):
        self.set_color(fg, bk)
        print(text, end="")

    def print_at(self, x, y, text):
        self.gotoXY(x, y)
        print(text, end="")

    def print(self, text):
        print(text, end="")

    def clear(self):
        sys.stdout.write(CODES["clear"])

    def gotoXY(self, x, y):
        sys.stdout.write(CODES["gotoxy"] % (y, x))

    def save_pos(self):
        sys.stdout.write(CODES["save"])

    def restore_pos(self):
        sys.stdout.write(CODES["restore"])

    def reset(self):
        sys.stdout.write(CODES["reset"])

    def move_left(self, c=1):
        sys.stdout.write(CODES["move_left"] % c)

    def move_right(self, c=1):
        sys.stdout.write(CODES["move_right"] % c)

    def move_up(self, c=1):
        sys.stdout.write(CODES["move_up"] % c)

    def move_down(self, c=1):
        sys.stdout.write(CODES["move_down"] % c)

    def columns(self):
        return int(os.getenv("COLUMNS", self.ncolumns))

    def lines(self):
        return int(os.getenv("LINES", self.nlines))

    def underline(self):
        sys.stdout.write(CODES["underline"])

    def underline_off(self):
        sys.stdout.write(CODES["underline_off"])

    def blink(self):
        sys.stdout.write(CODES["blink"])

    def blink_off(self):
        sys.stdout.write(CODES["blink_off"])

    def reverse(self):
        sys.stdout.write(CODES["reverse"])

    def reverse_off(self):
        sys.stdout.write(CODES["reverse_off"])

    def italic(self):
        sys.stdout.write(CODES["italic"])

    def italic_off(self):
        sys.stdout.write(CODES["italic_off"])

    def crossed(self):
        sys.stdout.write(CODES["crossed"])

    def crossed_off(self):
        sys.stdout.write(CODES["crossed_off"])

    def invisible(self):
        sys.stdout.write(CODES["invisible"])

    def reset_colors(self):
        self.default_background()
        self.default_foreground
        self.reset()

    def xterm256_set_fg_color(self, color):
        sys.stdout.write(ESCAPE + "38;5;%dm" % color)

    def xterm24bit_set_fg_color(self, r, g, b):
        sys.stdout.write(ESCAPE + "38;2;%d;%d;%dm" % (r, g, b))

    def xterm256_set_bk_color(self, color):
        sys.stdout.write(ESCAPE + "48;5;%dm" % color)

    def xterm24bit_set_bk_color(self, r, g, b):
        sys.stdout.write(ESCAPE + "48;2;%d;%d;%dm" % (r, g, b))

    def default_foreground(self):
        sys.stdout.write(ESCAPE + "39m")

    def default_background(self):
        sys.stdout.write(ESCAPE + "49m")
