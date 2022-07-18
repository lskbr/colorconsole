from __future__ import print_function
from colorconsole import terminal

screen = terminal.get_terminal()
screen.clear()
screen.set_title("Example 3")

if screen.type == "WIN" and not screen.new_windows_terminal:
    raise RuntimeError("24 bit mode not supported on Windows.")

screen.blink()
screen.underline()
screen.print_at(0, 0, "Color table 24 bits")
screen.reset()

c = 0
screen.gotoXY(0, 3)
try:
    for r in range(256):
        for g in range(256):
            for b in range(256):
                screen.xterm24bit_set_bk_color(r, g, b)
                screen.print(" ")
                c += 1
                if (c + 1) % 64 == 0:
                    print()
                if (c + 1) % 1024 == 0:
                    screen.gotoXY(0, 3)
    print()
    # Waits for a single key touch before ending.
    screen.getch()
except KeyboardInterrupt:
    pass
finally:
    screen.reset_colors()
