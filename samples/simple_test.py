import sys
from colorconsole import terminal

from colorconsole.terminal import color_numbers_to_names, colors, get_terminal


def test():
    t = terminal.get_terminal(conEmu=terminal.is_conemu())
    t.enable_unbuffered_input_mode()
    t.set_color(fg=2, bk=0)
    t.clear()
    t.gotoXY(0, 0)
    t.set_title("Testing output")
    # Terminal Type
    t.set_color(fg=2, bk=0)
    print(f"Terminal Type: {t.type}")
    print(f"Windows terminal: {t.new_windows_terminal}")
    print("\n            Foreground 111111")
    print("Background   0123456789012345")
    for b in range(8):
        t.reset()
        print("            ", end="")
        print(b, end="")
        for f in range(16):
            t.cprint(f, b, f % 10)
        print()
    # Color name mapping
    for b in range(16):
        t.gotoXY(50, b + 2)
        t.cprint(0, b, "       ")
        t.gotoXY(60, b + 2)
        t.cprint(colors["WHITE"], colors["BLACK"], color_numbers_to_names[b])
    # 256-colors
    t.print_at(70, 1, "0123456789ABCDEF")
    for line, x in enumerate("0123456789ABCDEF"):
        t.print_at(69, 2 + line, x)
    for color in range(256):
        t.xterm256_set_bk_color(color)
        t.xterm256_set_fg_color(~color)
        t.gotoXY(70 + color % 16, color // 16 + 2)
        t.print("X")
    # Special attributes
    t.set_color(fg=2, bk=0)
    print()
    t.blink()
    print("BLINK")
    t.blink_off()
    t.reverse()
    print("REVERSE")
    t.reverse_off()
    t.underline()
    print("underline")
    t.underline_off()
    t.italic()
    print("Italic")
    t.italic_off()
    t.crossed()
    print("Crossed")
    t.crossed_off()
    # Keyboard read (input)
    t.set_color(fg=2, bk=0)
    a = 0
    b = 0
    try:
        t.print_at(0, 15, "Keyboard input")
        while True:
            t.print_at(a % 30, 17, ".")
            if t.kbhit(0.1):
                ch = t.getch()
                t.print_at(0, 18, f"Last pressed: {str(ch):8s} - {ord(ch):5d}")
            a += 1
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        t.restore_buffered_mode()
        t.reset()
    t.clear()


if __name__ == "__main__":
    test()
