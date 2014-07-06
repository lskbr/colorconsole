from __future__ import print_function
from colorconsole import terminal

screen = terminal.get_terminal()
screen.clear()
screen.set_title("Example 3")

screen.print_at(0,0,"Color table 24 bits")

if screen.type == "WIN":
    raise RuntimeError("24 bit mode not supported on Windows.")

screen.gotoXY(0,3)
for r in range(0, 256, 16):
    for g in range(0, 256, 16):
        for b in range(0, 256, 16):
            screen.xterm24bit_set_bk_color(r,g,b)
            print("%02x%02x%02x" % (r,g,b), end="")            
print()    
screen.reset_colors()
# Waits for a single key touch before ending.
screen.getch()