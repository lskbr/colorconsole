import math
from colorconsole import terminal

screen = terminal.get_terminal(conEmu=terminal.is_conemu())
screen.set_title("Example 1")
screen.set_color(terminal.colors["WHITE"], terminal.colors["BLUE"])
screen.clear()

PI = math.pi
step = (2.0 * PI) / screen.columns()

for x in range(screen.columns()):
    screen.set_color(terminal.colors["YELLOW"], terminal.colors["RED"])
    screen.print_at(x, 11, "-")
    screen.set_color(2, 7)
    screen.print_at(x, 11 + math.sin(x * step) * 10, "S")
    screen.set_color(1, 2)
    screen.print_at(x, 11 + math.cos(x * step) * 10, "C")

screen.reset_colors()
# Waits for a single key touch before ending.
screen.getch()
