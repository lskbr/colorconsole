from __future__ import print_function
from colorconsole import terminal

screen = terminal.get_terminal()
screen.clear()
screen.set_title("Example 3")

if screen.type == "WIN":
    raise RuntimeError("24 bit mode not supported on Windows.")

screen.underline()
screen.blink()
screen.print_at(0,0,"Color table 24 bits")
screen.reset()

c=0
screen.gotoXY(0,3)
for r in range(256):
    for g in range(256):
        for b in range(256):
            screen.xterm24bit_set_bk_color(r,g,b)
            print(" ", end="")
            c+=1
            if (c+1)%64==0:
                print()
            if (c+1)%1024==0:
                screen.gotoXY(0,3)
print()    
screen.reset_colors()
# Waits for a single key touch before ending.
screen.getch()
