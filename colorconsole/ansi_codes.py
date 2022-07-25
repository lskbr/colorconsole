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
# https://docs.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences
# https://devblogs.microsoft.com/commandline/author/richturnmicrosoft-com/
# https://docs.microsoft.com/en-us/windows/console/setconsolemode


ESCAPE = "\x1b["
CODES = {
    "reset": ESCAPE + "0m",
    "bold": ESCAPE + "1m",
    "clear": ESCAPE + "2J",
    "clear_eol": ESCAPE + "K",
    "gotoxy": ESCAPE + "%d;%dH",
    "move_up": ESCAPE + "%dA",
    "move_down": ESCAPE + "%dB",
    "move_right": ESCAPE + "%dC",
    "move_left": ESCAPE + "%dD",
    "save": ESCAPE + "s",
    "restore": ESCAPE + "u",
    "dim": ESCAPE + "2m",
    "underline": ESCAPE + "4m",
    "underline_off": ESCAPE + "24m",
    "blink": ESCAPE + "5m",
    "blink_off": ESCAPE + "25m",
    "reverse": ESCAPE + "7m",
    "reverse_off": ESCAPE + "27m",
    "invisible": ESCAPE + "8m",
    "italic": ESCAPE + "3m",
    "italic_off": ESCAPE + "23m",
    "crossed": ESCAPE + "9m",
    "crossed_off": ESCAPE + "29m",
}

COLORS_FG = {
    0: "0;30m",  # black
    1: "0;34m",  # blue
    2: "0;32m",  # green
    3: "0;36m",  # cyan
    4: "0;31m",  # red
    5: "0;35m",  # magenta
    6: "0;33m",  # yellow
    7: "0;37m",  # white
    8: "1;30m",  # grey
    9: "1;34m",
    10: "1;32m",  # bright green
    11: "1;36m",
    12: "1;31m",  # bright blue
    13: "1;35m",
    14: "1;33m",  # bright cyan
    15: "1;37m",  # white
}

COLORS_BK = {
    0: "40m",  # black
    1: "44m",  # blue
    2: "42m",  # green
    3: "46m",  # cyan
    4: "41m",  # red
    5: "45m",  # magenta
    6: "43m",  # yellow
    7: "47m",  # white
    8: "100m",
    9: "104m",
    10: "102m",
    11: "106m",
    12: "101m",
    13: "105m",
    14: "103m",
    15: "107m",
}
