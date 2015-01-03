#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#    colorconsole
#    Copyright (C) 2014 Sylvain MOUQUET
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

# Added for Python 2.6 compatibility
from __future__ import print_function
import os,sys
from ctypes import windll, Structure, c_short, c_ushort, byref, c_char_p, c_uint, c_wchar_p, c_char, c_uint16
import time

def get_terminal(conEmu=False):
    if os.name == "posix":
        import colorconsole.ansi       
        return colorconsole.ansi.Terminal()
    elif os.name == "nt":
        if conEmu:
          import colorconsole.conemu
          return colorconsole.conemu.Terminal()
        else:
          import colorconsole.win        
          return colorconsole.win.Terminal()  
    else:
        raise RuntimeError("Unknown or unsupported terminal")


def test():
    t = get_terminal()
    t.enable_unbuffered_input_mode()
    t.clear()
    t.set_title(u"Test buffer UTF8 éà@èù")

    width  = t.columns() #100
    height = t.lines()   #50

    t.init_buffer(width, height)
    t.gotoXY(0,0)

    try:
        while(True):
            #for i in range(0, width * height):
            #    t.set_buffer_char(i, i % 10, 0, 255)

            s=str(int(time.time()))
            t.set_buffer_string(1, 10, s, 10, 0)
            t.set_buffer_string(0, 0, u"line0", 10, 0)
            t.set_buffer_string(0, 1, u"line1", 10, 0)
            t.set_buffer_string(0, 2, u"line2", 10, 0)
            t.set_buffer_string(0, 5, u"éà@èù", 10, 0)
            t.print_buffer()
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    t.clear()
    t.reset()
    t.restore_buffered_mode()
               
if __name__ == "__main__":
    print ("run")
    test()