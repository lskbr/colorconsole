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

from ctypes import windll, Structure, c_short, c_ushort, c_uint, c_wchar_p

SHORT = c_short
WORD = c_ushort
DWORD = c_uint


class COORD(Structure):
    """struct in wincon.h."""

    _fields_ = [("X", SHORT), ("Y", SHORT)]


class SMALL_RECT(Structure):
    """struct in wincon.h."""

    _fields_ = [("Left", SHORT), ("Top", SHORT), ("Right", SHORT), ("Bottom", SHORT)]


class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    """struct in wincon.h."""

    _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", WORD),
        ("srWindow", SMALL_RECT),
        ("dwMaximumWindowSize", COORD),
    ]


cstring_p = c_wchar_p

SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo
SetConsoleTitle = windll.kernel32.SetConsoleTitleW
GetConsoleTitle = windll.kernel32.GetConsoleTitleW
SetConsoleCursorPosition = windll.kernel32.SetConsoleCursorPosition
FillConsoleOutputCharacter = windll.kernel32.FillConsoleOutputCharacterA
FillConsoleOutputAttribute = windll.kernel32.FillConsoleOutputAttribute
WaitForSingleObject = windll.kernel32.WaitForSingleObject
ReadConsoleA = windll.kernel32.ReadConsoleA
WriteConsoleW = windll.kernel32.WriteConsoleW
GetConsoleMode = windll.kernel32.GetConsoleMode
SetConsoleMode = windll.kernel32.SetConsoleMode
GetStdHandle = windll.kernel32.GetStdHandle

ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
