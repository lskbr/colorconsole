from colorconsole import terminal

screen = terminal.get_terminal(conEmu=terminal.is_conemu())
screen.clear()
screen.set_title("Example 2")

screen.print_at(0, 0, "Color table")
try:
    if screen.type == "WIN" and not screen.new_windows_terminal:
        for x in range(16):
            screen.gotoXY(0, x + 1)
            screen.cprint(15, 0, "%2d" % x)
            screen.gotoXY(3, x + 1)
            screen.cprint(x, x, " " * 20)
    else:
        screen.gotoXY(0, 3)
        for x in range(256):
            screen.xterm256_set_fg_color(x)
            print("%02x" % x, end="" if (x + 1) % 32 != 0 else "\n")

        screen.gotoXY(0, 12)
        for x in range(256):
            screen.xterm256_set_bk_color(x)
            print("%02x" % x, end="" if (x + 1) % 32 != 0 else "\n")
        print()
except KeyboardInterrupt:
    pass
finally:
    screen.reset_colors()
