from colorconsole import terminal

# Printing Emojis

SNOWMAN = "\u26C4"
FERRY = "\U0001F6F6"
CAR = "\U0001F6FB"
MOTO = "\U0001F6F5"
SCOOTER = "\U0001F6F4"
SKATE = "\U0001F6F9"
PANDA = "\U0001F43C"

DICE = ["\u2680", "\u2681", "\u2682", "\u2683", "\u2684", "\u2685"]
CASA = "\U0001F3E0"
HOTEL = "\U0001F3E8"

screen = terminal.get_terminal(conEmu=terminal.is_conemu())
screen.clear()
screen.gotoXY(0, 0)
print("Colorconsole/terminal print:")
screen.print(SNOWMAN)
screen.print(FERRY)
screen.print(CAR)
screen.print(f"\n{SNOWMAN} {FERRY} {CAR} {MOTO} {SCOOTER} {PANDA}")
print("\nPython print:")
print(SNOWMAN, end="")
print(FERRY, end="")
print(CAR, end="")
print(f"\n{SNOWMAN} {FERRY} {CAR} {MOTO} {SCOOTER} {PANDA}")


SMILE = "\U0001F600"

for x in range(40, 60, 4):
    for y in range(5, 10):
        screen.print_at(x, y, SMILE)
screen.getch()
