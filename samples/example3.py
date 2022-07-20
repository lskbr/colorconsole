from colorconsole import terminal

screen = terminal.get_terminal(conEmu=terminal.is_conemu())
screen.clear()
screen.set_title("Example 3")

# The standard Windows console does not support 24-bit color,
# but the Windows Terminal does (windows 10 and 11)
if screen.type == "WIN" and not screen.new_windows_terminal:
    raise RuntimeError(
        "24 bit mode not supported on Windows console. Try with the Windows Terminal."
    )

screen.blink()
screen.underline()
screen.print_at(0, 0, "Color table 24 bits")
screen.reset()

c = 0
screen.gotoXY(0, 3)
try:
    screen.hide_cursor()
    for r in range(256):
        for g in range(256):
            c = 0
            for b in range(256):
                screen.xterm24bit_set_bk_color(0, 0, 0)
                screen.print_at(0, 1, f"RGB = ({r},{g},{b})".ljust(30))
                screen.xterm24bit_set_bk_color(r, g, b)
                screen.print_at((c % 16) * 4, c // 16 + 5, "    ")
                c += 1
    print()
    # Waits for a single key touch before ending.
    screen.getch()
except KeyboardInterrupt:
    pass
finally:
    screen.show_cursor()
    screen.reset_colors()
