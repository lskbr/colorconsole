from __future__ import print_function
from colorconsole import terminal

screen = terminal.get_terminal()
screen.clear()
screen.print_at(0,0,"Color table")

if screen.type == "WIN":
    for x in range(16):
        screen.gotoXY(0,x+1)
        screen.cprint(15,0, "%2d"%x)
        screen.gotoXY(3,x+1)
        screen.cprint(x,x, " " * 20)
else:
    screen.gotoXY(0,3)
    for x in range(256):
        screen.xterm256_set_fg_color(x)
        print("%02x" % x, end="" if (x+1)%32!=0 else "\n")
        
    screen.gotoXY(0,12)
    for x in range(256):
        screen.xterm256_set_bk_color(x)
        print("%02x" % x, end="" if (x+1)%32!=0 else "\n")
    print()    
screen.reset_colors()

