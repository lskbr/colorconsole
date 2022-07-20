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


def make_ansi():
    import colorconsole.ansi

    return colorconsole.ansi.Terminal()


def make_conemu():
    import colorconsole.conemu

    return colorconsole.conemu.Terminal()


def make_winconsole():
    import colorconsole.win

    return colorconsole.win.Terminal()


def is_conemu():
    return False if os.getenv("ConEmuPid") is None else True


def get_terminal(conEmu=False):
    if os.name == "posix":
        return make_ansi()
    elif os.name == "nt":
        if conEmu:
            return make_conemu()
        else:
            return make_winconsole()
    else:
        raise RuntimeError("Unknown or unsupported terminal")
