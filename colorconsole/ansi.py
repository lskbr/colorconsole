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

# Added for Python 2.6 compatibility
from __future__ import print_function
import os
import sys
import termios
from select import select


class Terminal:
    escape = "\x1b["
    codes = {
             "reset": escape + "0m",
             "bold": escape + "01m",
             "clear": escape + "2J",
             "clear_eol": escape + "K",
             "gotoxy": escape + "%d;%dH",
             "move_up": escape + "%dA",
             "move_down": escape + "%dB",
             "move_right": escape + "%dC",
             "move_left": escape + "%dD",
             "save": escape + "s",
             "restore": escape + "u",
             "dim": escape + "2m",
             "underline": escape + "4m",
             "blink": escape + "5m",
             "reverse": escape + "7m",
             "invisible": escape + "8m",
            }

    colors_fg = {
                 0: "30m",
                 1: "31m",
                 2: "32m",
                 3: "33m",
                 4: "34m",
                 5: "35m",
                 6: "36m",
                 7: "37m",
                 8: "1;30m",
                 9: "1;31m",
                 10: "1;32m",
                 11: "1;33m",
                 12: "1;34m",
                 13: "1;35m",
                 14: "1;36m",
                 15: "1;37m"
                }

    colors_bk = {
                 0: "40m",
                 1: "41m",
                 2: "42m",
                 3: "43m",
                 4: "44m",
                 5: "45m",
                 6: "46m",
                 7: "47m",
                }

    def __init__(self):
        self.fg = None
        self.bk = None
        self.havecolor = 1
        self.dotitles = 1
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
        self.ncolumns = 80
        self.nlines = 24
        if "TERM" in os.environ:
            self.type = os.environ["TERM"]
        else:
            self.type = "UNKNOWN-ANSI"

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
            sys.stdout.write(Terminal.escape + Terminal.colors_fg[fg])
        if bk is not None:
            sys.stdout.write(Terminal.escape + Terminal.colors_bk[bk])

    def set_title(self, title):
        if self.type in ["xterm", "Eterm", "aterm", "rxvt", "xterm-color"]:
            sys.stderr.write("\x1b]1;\x07\x1b]2;" + str(title) + "\x07")
            sys.stderr.flush()

    def cprint(self, fg, bk, text):
        self.set_color(fg, bk)
        print (text, end="")

    def print_at(self, x, y, text):
            self.gotoXY(x, y)
            print(text, end="")

    def clear(self):
        sys.stdout.write(Terminal.codes["clear"])

    def gotoXY(self, x, y):
        sys.stdout.write(Terminal.codes["gotoxy"] % (y, x))

    def save_pos(self):
        sys.stdout.write(Terminal.codes["save"])

    def restore_pos(self):
        sys.stdout.write(Terminal.codes["restore"])

    def reset(self):
        sys.stdout.write(Terminal.codes["reset"])

    def move_left(self, c=1):
        sys.stdout.write(Terminal.codes["move_left"] % c)

    def move_right(self, c=1):
        sys.stdout.write(Terminal.codes["move_right"] % c)

    def move_up(self, c=1):
        sys.stdout.write(Terminal.codes["move_up"] % c)

    def move_down(self, c=1):
        sys.stdout.write(Terminal.codes["move_down"] % c)

    def columns(self):
        return int(os.getenv("COLUMNS", self.ncolumns))

    def lines(self):
        return int(os.getenv("LINES", self.nlines))

    def underline(self):
        sys.stdout.write(Terminal.codes["underline"])

    def blink(self):
        sys.stdout.write(Terminal.codes["blink"])

    def reverse(self):
        sys.stdout.write(Terminal.codes["reverse"])

    def invisible(self):
        sys.stdout.write(Terminal.codes["invisible"])

    def reset_colors(self):
        self.default_background()
        self.default_foreground
        self.reset()

    def xterm256_set_fg_color(self, color):
        sys.stdout.write(Terminal.escape+"38;5;%dm" % color)

    def xterm24bit_set_fg_color(self, r, g, b):
        sys.stdout.write(Terminal.escape+"38;2;%d;%d;%dm" % (r, g, b))

    def xterm256_set_bk_color(self, color):
        sys.stdout.write(Terminal.escape+"48;5;%dm" % color)

    def xterm24bit_set_bk_color(self, r, g, b):
        sys.stdout.write(Terminal.escape+"48;2;%d;%d;%dm" % (r, g, b))

    def default_foreground(self):
        sys.stdout.write(Terminal.escape+"39m")

    def default_background(self):
        sys.stdout.write(Terminal.escape+"49m")
