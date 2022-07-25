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
from typing import List, Optional
from ctypes import (
    c_bool,
    windll,
    Structure,
    Union,
    c_short,
    c_ushort,
    c_uint,
    c_wchar_p,
    c_char_p,
    wintypes,
)

from ctypes.wintypes import BOOL, CHAR, DWORD, HANDLE, SHORT, UINT, WCHAR, WORD

# SHORT = c_short
# WORD = c_ushort
# DWORD = c_uint
# BOOL = c_bool


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


class CONSOLE_CURSOR_INFO(Structure):
    _fields_ = [("dwSize", DWORD), ("bVisible", BOOL)]


# From Textual
# https://github.com/Textualize/textual/blob/da8f842f144f0eb91885c2ac4d2ae53f8d4fa5e8/src/textual/drivers/win32.py#L228


class uChar(Union):
    """https://docs.microsoft.com/en-us/windows/console/key-event-record-str"""

    _fields_ = [
        ("AsciiChar", CHAR),
        ("UnicodeChar", WCHAR),
    ]


class KEY_EVENT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/key-event-record-str"""

    _fields_ = [
        ("bKeyDown", BOOL),
        ("wRepeatCount", WORD),
        ("wVirtualKeyCode", WORD),
        ("wVirtualScanCode", WORD),
        ("uChar", uChar),
        ("dwControlKeyState", DWORD),
    ]


class MOUSE_EVENT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/mouse-event-record-str"""

    _fields_ = [
        ("dwMousePosition", COORD),
        ("dwButtonState", DWORD),
        ("dwControlKeyState", DWORD),
        ("dwEventFlags", DWORD),
    ]


class WINDOW_BUFFER_SIZE_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/window-buffer-size-record-str"""

    _fields_ = [("dwSize", COORD)]


class MENU_EVENT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/menu-event-record-str"""

    _fields_ = [("dwCommandId", UINT)]


class FOCUS_EVENT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/focus-event-record-str"""

    _fields_ = [("bSetFocus", BOOL)]


class InputEvent(Union):
    """https://docs.microsoft.com/en-us/windows/console/input-record-str"""

    _fields_ = [
        ("KeyEvent", KEY_EVENT_RECORD),
        ("MouseEvent", MOUSE_EVENT_RECORD),
        ("WindowBufferSizeEvent", WINDOW_BUFFER_SIZE_RECORD),
        ("MenuEvent", MENU_EVENT_RECORD),
        ("FocusEvent", FOCUS_EVENT_RECORD),
    ]


class INPUT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/input-record-str"""

    _fields_ = [("EventType", wintypes.WORD), ("Event", InputEvent)]


# End from textual

SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo
SetConsoleScreenBufferSize = windll.kernel32.SetConsoleScreenBufferSize
SetConsoleTitle = windll.kernel32.SetConsoleTitleW
GetConsoleTitle = windll.kernel32.GetConsoleTitleW
SetConsoleCursorPosition = windll.kernel32.SetConsoleCursorPosition
FillConsoleOutputCharacter = windll.kernel32.FillConsoleOutputCharacterA
FillConsoleOutputAttribute = windll.kernel32.FillConsoleOutputAttribute
WaitForSingleObject = windll.kernel32.WaitForSingleObject
ReadConsoleA = windll.kernel32.ReadConsoleA
WriteConsoleW = windll.kernel32.WriteConsoleW
WriteConsoleA = windll.kernel32.WriteConsoleA
GetConsoleMode = windll.kernel32.GetConsoleMode
SetConsoleMode = windll.kernel32.SetConsoleMode
GetStdHandle = windll.kernel32.GetStdHandle
SetConsoleOutputCP = windll.kernel32.SetConsoleOutputCP
SetConsoleCP = windll.kernel32.SetConsoleCP
GetConsoleCursorInfo = windll.kernel32.GetConsoleCursorInfo
SetConsoleCursorInfo = windll.kernel32.SetConsoleCursorInfo

ReadConsoleInputW = windll.kernel32.ReadConsoleInputW
WaitForMultipleObjects = windll.kernel32.WaitForMultipleObjects

ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
ENABLE_WINDOW_INPUT = 0x0008
CP_UTF8 = 65001

# Wait return values: https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject
WAIT_OBJECT_0 = 0

# Input events: https://docs.microsoft.com/en-us/windows/console/input-record-str
KEY_EVENT = 0x0001
MOUSE_EVENT = 0x0002
WINDOW_BUFFER_SIZE_EVENT = 0x0004
MENU_EVENT = 0x0008
FOCUS_EVENT = 0x0010

# From Textual (adapted)
# #https://github.com/Textualize/textual/blob/da8f842f144f0eb91885c2ac4d2ae53f8d4fa5e8/src/textual/drivers/win32.py#L178:

WAIT_TIMEOUT = 0x00000102


def wait_for_handles(handles: List[HANDLE], timeout: int = -1) -> Optional[HANDLE]:
    """
    Waits for multiple handles. (Similar to 'select') Returns the handle which is ready.
    Returns `None` on timeout.
    http://msdn.microsoft.com/en-us/library/windows/desktop/ms687025(v=vs.85).aspx
    Note that handles should be a list of `HANDLE` objects, not integers. See
    this comment in the patch by @quark-zju for the reason why:
        ''' Make sure HANDLE on Windows has a correct size
        Previously, the type of various HANDLEs are native Python integer
        types. The ctypes library will treat them as 4-byte integer when used
        in function arguments. On 64-bit Windows, HANDLE is 8-byte and usually
        a small integer. Depending on whether the extra 4 bytes are zero-ed out
        or not, things can happen to work, or break. '''
    This function returns either `None` or one of the given `HANDLE` objects.
    (The return value can be tested with the `is` operator.)
    """
    arrtype = HANDLE * len(handles)
    handle_array = arrtype(*handles)

    ret: int = WaitForMultipleObjects(
        len(handle_array), handle_array, BOOL(False), DWORD(timeout)
    )

    if ret == WAIT_TIMEOUT:
        return None
    else:
        return handles[ret]
