from colorconsole import terminal


def resize(screen, x, y):
    message = f"New size: {x}x{y}"
    screen.clear()
    screen.print_at((x - len(message)) // 2, y // 2, message)
    screen.print_at(1, 0, "LU")
    screen.print_at(x - 2, 1, "RU")
    screen.print_at(1, y - 1, "LD")
    screen.print_at(x - 2, y - 1, "RD")
    screen.print_at(1, 2, f"Current size: {screen.columns()}x{screen.lines()}")


screen = terminal.get_terminal(conEmu=terminal.is_conemu())
try:
    # screen.set_console_size(150, 50)
    screen.clear()
    screen.enable_window_events()
    screen.print_at(10, 10, "Please change the window size")
    screen.print_at(10, 11, f"Current size: {screen.columns()}x{screen.lines()}")
    screen.on_resize = lambda x, y: resize(screen, x, y)

    screen.getch()
finally:
    screen.disable_windows_events()
