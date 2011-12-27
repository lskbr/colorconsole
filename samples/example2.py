from colorconsole import terminal

screen = terminal.get_terminal()
screen.clear()
screen.gotoXY(3,0)

screen.cprint(15,0,"Color table")
for x in range(16):
	screen.gotoXY(0,x+1)
	screen.cprint(15,0, "%2d"%x)
	screen.gotoXY(3,x+1)
	screen.cprint(x,x, " " * 20)

screen.reset()

