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
from ctypes import byref

from .ansi_codes import ESCAPE, CODES
from .win_common import (
    SetConsoleTextAttribute,
    GetConsoleScreenBufferInfo,
    SetConsoleTitle,
    SetConsoleCursorPosition,
    FillConsoleOutputCharacter,
    FillConsoleOutputAttribute,
    WriteConsoleW,
    GetStdHandle,
    CONSOLE_SCREEN_BUFFER_INFO,
    DWORD,
    COORD,
    cstring_p,
    GetConsoleMode,
    SetConsoleMode,
    ENABLE_VIRTUAL_TERMINAL_INPUT,
    ENABLE_VIRTUAL_TERMINAL_PROCESSING,
)


class Terminal:
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    WAIT_TIMEOUT = 0x00000102
    WAIT_OBJECT_0 = 0
    # Color pallete for Windows terminal xterm-256 colors mode
    WT_COLORS_256 = [
        "0;0;0",  # 0
        "128;0;0",  # 1
        "0;128;0",  # 2
        "128;128;0",  # 3
        "0;0;128",  # 4
        "128;0;128",  # 5
        "0;128;128",  # 6
        "192;192;192",  # 7
        "128;128;128",  # 8
        "255;0;0",  # 9
        "0;255;0",  # 10
        "255;255;0",  # 11
        "0;0;255",  # 12
        "255;0;255",  # 13
        "0;255;255",  # 14
        "255;255;255",  # 15
        "0;0;0",  # 16
        "0;0;95",  # 17
        "0;0;135",  # 18
        "0;0;175",  # 19
        "0;0;215",  # 20
        "0;0;255",  # 21
        "0;95;0",  # 22
        "0;95;95",  # 23
        "0;95;135",  # 24
        "0;95;175",  # 25
        "0;95;215",  # 26
        "0;95;255",  # 27
        "0;135;0",  # 28
        "0;135;95",  # 29
        "0;135;135",  # 30
        "0;135;175",  # 31
        "0;135;215",  # 32
        "0;135;255",  # 33
        "0;175;0",  # 34
        "0;175;95",  # 35
        "0;175;135",  # 36
        "0;175;175",  # 37
        "0;175;215",  # 38
        "0;175;255",  # 39
        "0;215;0",  # 40
        "0;215;95",  # 41
        "0;215;135",  # 42
        "0;215;175",  # 43
        "0;215;215",  # 44
        "0;215;255",  # 45
        "0;255;0",  # 46
        "0;255;95",  # 47
        "0;255;135",  # 48
        "0;255;175",  # 49
        "0;255;215",  # 50
        "0;255;255",  # 51
        "95;0;0",  # 52
        "95;0;95",  # 53
        "95;0;135",  # 54
        "95;0;175",  # 55
        "95;0;215",  # 56
        "95;0;255",  # 57
        "95;95;0",  # 58
        "95;95;95",  # 59
        "95;95;135",  # 60
        "95;95;175",  # 61
        "95;95;215",  # 62
        "95;95;255",  # 63
        "95;135;0",  # 64
        "95;135;95",  # 65
        "95;135;135",  # 66
        "95;135;175",  # 67
        "95;135;215",  # 68
        "95;135;255",  # 69
        "95;175;0",  # 70
        "95;175;95",  # 71
        "95;175;135",  # 72
        "95;175;175",  # 73
        "95;175;215",  # 74
        "95;175;255",  # 75
        "95;215;0",  # 76
        "95;215;95",  # 77
        "95;215;135",  # 78
        "95;215;175",  # 79
        "95;215;215",  # 80
        "95;215;255",  # 81
        "95;255;0",  # 82
        "95;255;95",  # 83
        "95;255;135",  # 84
        "95;255;175",  # 85
        "95;255;215",  # 86
        "95;255;255",  # 87
        "135;0;0",  # 88
        "135;0;95",  # 89
        "135;0;135",  # 90
        "135;0;175",  # 91
        "135;0;215",  # 92
        "135;0;255",  # 93
        "135;95;0",  # 94
        "135;95;95",  # 95
        "135;95;135",  # 96
        "135;95;175",  # 97
        "135;95;215",  # 98
        "135;95;255",  # 99
        "135;135;0",  # 100
        "135;135;95",  # 101
        "135;135;135",  # 102
        "135;135;175",  # 103
        "135;135;215",  # 104
        "135;135;255",  # 105
        "135;175;0",  # 106
        "135;175;95",  # 107
        "135;175;135",  # 108
        "135;175;175",  # 109
        "135;175;215",  # 110
        "135;175;255",  # 111
        "135;215;0",  # 112
        "135;215;95",  # 113
        "135;215;135",  # 114
        "135;215;175",  # 115
        "135;215;215",  # 116
        "135;215;255",  # 117
        "135;255;0",  # 118
        "135;255;95",  # 119
        "135;255;135",  # 120
        "135;255;175",  # 121
        "135;255;215",  # 122
        "135;255;255",  # 123
        "175;0;0",  # 124
        "175;0;95",  # 125
        "175;0;135",  # 126
        "175;0;175",  # 127
        "175;0;215",  # 128
        "175;0;255",  # 129
        "175;95;0",  # 130
        "175;95;95",  # 131
        "175;95;135",  # 132
        "175;95;175",  # 133
        "175;95;215",  # 134
        "175;95;255",  # 135
        "175;135;0",  # 136
        "175;135;95",  # 137
        "175;135;135",  # 138
        "175;135;175",  # 139
        "175;135;215",  # 140
        "175;135;255",  # 141
        "175;175;0",  # 142
        "175;175;95",  # 143
        "175;175;135",  # 144
        "175;175;175",  # 145
        "175;175;215",  # 146
        "175;175;255",  # 147
        "175;215;0",  # 148
        "175;215;95",  # 149
        "175;215;135",  # 150
        "175;215;175",  # 151
        "175;215;215",  # 152
        "175;215;255",  # 153
        "175;255;0",  # 154
        "175;255;95",  # 155
        "175;255;135",  # 156
        "175;255;175",  # 157
        "175;255;215",  # 158
        "175;255;255",  # 159
        "215;0;0",  # 160
        "215;0;95",  # 161
        "215;0;135",  # 162
        "215;0;175",  # 163
        "215;0;215",  # 164
        "215;0;255",  # 165
        "215;95;0",  # 166
        "215;95;95",  # 167
        "215;95;135",  # 168
        "215;95;175",  # 169
        "215;95;215",  # 170
        "215;95;255",  # 171
        "215;135;0",  # 172
        "215;135;95",  # 173
        "215;135;135",  # 174
        "215;135;175",  # 175
        "215;135;215",  # 176
        "215;135;255",  # 177
        "215;175;0",  # 178
        "215;175;95",  # 179
        "215;175;135",  # 180
        "215;175;175",  # 181
        "215;175;215",  # 182
        "215;175;255",  # 183
        "215;215;0",  # 184
        "215;215;95",  # 185
        "215;215;135",  # 186
        "215;215;175",  # 187
        "215;215;215",  # 188
        "215;215;255",  # 189
        "215;255;0",  # 190
        "215;255;95",  # 191
        "215;255;135",  # 192
        "215;255;175",  # 193
        "215;255;215",  # 194
        "215;255;255",  # 195
        "255;0;0",  # 196
        "255;0;95",  # 197
        "255;0;135",  # 198
        "255;0;175",  # 199
        "255;0;215",  # 200
        "255;0;255",  # 201
        "255;95;0",  # 202
        "255;95;95",  # 203
        "255;95;135",  # 204
        "255;95;175",  # 205
        "255;95;215",  # 206
        "255;95;255",  # 207
        "255;135;0",  # 208
        "255;135;95",  # 209
        "255;135;135",  # 210
        "255;135;175",  # 211
        "255;135;215",  # 212
        "255;135;255",  # 213
        "255;175;0",  # 214
        "255;175;95",  # 215
        "255;175;135",  # 216
        "255;175;175",  # 217
        "255;175;215",  # 218
        "255;175;255",  # 219
        "255;215;0",  # 220
        "255;215;95",  # 221
        "255;215;135",  # 222
        "255;215;175",  # 223
        "255;215;215",  # 224
        "255;215;255",  # 225
        "255;255;0",  # 226
        "255;255;95",  # 227
        "255;255;135",  # 228
        "255;255;175",  # 229
        "255;255;215",  # 230
        "255;255;255",  # 231
        "8;8;8",  # 232
        "18;18;18",  # 233
        "28;28;28",  # 234
        "38;38;38",  # 235
        "48;48;48",  # 236
        "58;58;58",  # 237
        "68;68;68",  # 238
        "78;78;78",  # 239
        "88;88;88",  # 240
        "98;98;98",  # 241
        "108;108;108",  # 242
        "118;118;118",  # 243
        "128;128;128",  # 244
        "138;138;138",  # 245
        "148;148;148",  # 246
        "158;158;158",  # 247
        "168;168;168",  # 248
        "178;178;178",  # 249
        "188;188;188",  # 250
        "198;198;198",  # 251
        "208;208;208",  # 252
        "218;218;218",  # 253
        "228;228;228",  # 254
        "238;238;238",  # 255
    ]

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
        if self.new_windows_terminal:
            self.enable_virtual_terminal_processing()

    def enable_virtual_terminal_processing(self):
        z = DWORD()
        GetConsoleMode(self.stdout_handle, byref(z))
        z = DWORD(z.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
        SetConsoleMode(self.stdout_handle, z)

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

    def print(self, text):
        self.win_print(text)

    def clear(self):  # From kb q99261
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
        self.gotoXY(ax + dx, ay + dy)

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

    def underline(self):
        if self.new_windows_terminal:
            sys.stdout.write(CODES["underline"])
            sys.stdout.flush()

    def underline_off(self):
        if self.new_windows_terminal:
            sys.stdout.write(CODES["underline_off"])
            sys.stdout.flush()

    def blink(self):
        if self.new_windows_terminal:
            sys.stdout.write(CODES["blink"])
            sys.stdout.flush()

    def blink_off(self):
        if self.new_windows_terminal:
            sys.stdout.write(CODES["blink_off"])
            sys.stdout.flush()

    def reverse(self):
        if self.new_windows_terminal:
            sys.stdout.write(CODES["reverse"])
            sys.stdout.flush()

    def reverse_off(self):
        if self.new_windows_terminal:
            sys.stdout.write(CODES["reverse_off"])
            sys.stdout.flush()

    def italic(self):
        if self.new_windows_terminal:
            sys.stdout.write(CODES["italic"])
            sys.stdout.flush()

    def italic_off(self):
        if self.new_windows_terminal:
            sys.stdout.write(CODES["italic_off"])
            sys.stdout.flush()

    def crossed(self):
        if self.new_windows_terminal:
            sys.stdout.write(CODES["crossed"])
            sys.stdout.flush()

    def crossed_off(self):
        if self.new_windows_terminal:
            sys.stdout.write(CODES["crossed_off"])
            sys.stdout.flush()

    def invisible(self):
        if self.new_windows_terminal:
            sys.stdout.write(CODES["invisible"])
            sys.stdout.flush()

    def reset_colors(self):
        self.reset()

    def win_print(self, x):
        if type(x) != str:
            x = str(x)
        length = len(x)
        w = DWORD(0)
        WriteConsoleW(self.stdout_handle, cstring_p(x), length, byref(w), None)

    def xterm256_set_fg_color(self, color):
        if self.new_windows_terminal:
            rgb = self.WT_COLORS_256[color]
            sys.stdout.write(ESCAPE + f"38;2;{rgb}m")
            sys.stdout.flush()

    def xterm256_set_bk_color(self, color):
        if self.new_windows_terminal:
            rgb = self.WT_COLORS_256[color]
            sys.stdout.write(ESCAPE + f"48;2;{rgb}m")
            sys.stdout.flush()

    def xterm24bit_set_fg_color(self, r, g, b):
        if self.new_windows_terminal:
            sys.stdout.write(ESCAPE + "38;2;%d;%d;%dm" % (r, g, b))
            sys.stdout.flush()

    def xterm24bit_set_bk_color(self, r, g, b):
        if self.new_windows_terminal:
            sys.stdout.write(ESCAPE + "48;2;%d;%d;%dm" % (r, g, b))
            sys.stdout.flush()

    def default_foreground(self):
        if self.new_windows_terminal:
            sys.stdout.write(ESCAPE + "39m")

    def default_background(self):
        sys.stdout.write(ESCAPE + "49m")
