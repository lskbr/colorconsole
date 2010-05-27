# ColorConsole
#
# Inspired on output.py from Gentoo and 
# http://code.activestate.com/recipes/572182-how-to-implement-kbhit-on-linux/
#

import os,sys, termios, atexit
from select import select


colors= { "BLACK"   : 0,
          "BLUE"    : 1,
          "GREEN"   : 2,
          "CYAN"    : 3,
          "RED"     : 4,
          "PURPLE"  : 5,
          "BROWN"   : 6,
          "LGREY"   : 7,
          "DGRAY"   : 8,
          "LBLUE"   : 9,
          "LGREEN"  : 10,
          "LCYAN"   : 11,
          "LRED"    : 12,
          "LPURPLE" : 13,
          "YELLOW"  : 14,
          "WHITE"   : 15  }

def get_terminal():
    if os.name == "nt":
        return TerminalWindows()
    if os.name == "posix":
        return TerminalANSIPosix()
    else:
        return None # Should raise exception!


class TerminalWindows:
    def __init__(self):
        self.fg = None
        self.bk = None
        self.havecolor = 1
        self.dotitles = 1
        import msvcrt
        import ctypes
        from ctypes import windll, Structure, c_short, c_ushort, byref, c_char_p, c_uint
        self.SHORT = c_short
        self.WORD = c_ushort
        
        self.stdout_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        self.SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
        self.GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo
        self.SetConsoleTitle = windll.kernel32.SetConsoleTitleA
        self.GetConsoleTitle = windll.kernel32.GetConsoleTitleA
        self.GetConsoleCP = windll.kernel32.GetConsoleCP
        self.SetConsoleCP = windll.kernel32.SetConsoleCP
        
    def restore_buffered_mode(self):
        pass


    def enable_unbuffered_input_mode(self):
        pass

    def putch(self, ch):
        msvcrt.putc(ch)

    def getch(self):
        return msvcrt.getc()

    def getche(self):
        return msvcrt.getche()

    def kbhit(self, timeout=0):
        return msvcrt.kbhit()

    def no_colors(self):
        self.havecolor = 0    

    def set_color(self, fg = None, bk = None):
        actual = self.__get_text_attr()
        if fg == None:
            fg = actual & 0x000F
        if bk == None:
            bk = actual & 0x00F0
        else:
            bk <<=4

        self.__set_text_attr(fg + bk)
        
    def __get_text_attr(self):
          csbi = self.CONSOLE_SCREEN_BUFFER_INFO()
          self.GetConsoleScreenBufferInfo(self.stdout_handle, byref(csbi))
          return csbi.wAttributes

    def __set_text_attr(self):
          self.SetConsoleTextAttribute(stdout_handle, color)

    def set_title(self, title):
        ctitle = c_char_p(title)
        self.SetConsoleTitle(ctitle)

    def cprint(self, fg, bk, text):
        self.set_color(fg, bk)
        print (text,end="")

    def print_at(self, x, y, text):
            self.gotoXY(x, y)
            print(text,end="")

    def clear(self):
        pass

    def gotoXY(self, x,y):
        pass

    def save_pos(self):
        pass

    def restore_pos(self):
        pass

    def reset(self):
        pass

    def move_left(self, c = 1):
        pass

    def move_right(self, c = 1):
        pass

    def move_up(self, c = 1):
        pass

    def move_down(self, c = 1):
        pass

    def columns(self):
        pass
        
    def lines(self):
        pass



class TerminalANSIPosix:
    escape = "\x1b["
    codes={}
    codes["reset"]="\x1b[0m"
    codes["bold"]="\x1b[01m"
    codes["clear"]="\x1b[2J"
    codes["clear_eol"] = "\x1b[K"
    codes["gotoxy"] = "\x1b[%d;%dH"
    codes["move_up"] = "\x1b[%dA"
    codes["move_down"] = "\x1b[%dB"
    codes["move_right"] = "\x1b[%dC"
    codes["move_left"] = "\x1b[%dD"
    codes["save"] = "\x1b[s"
    codes["restore"] = "\x1b[u"
    
    colors_fg = { 0 : "30m",
                  1 : "31m",
                  2 : "32m",
                  3 : "33m",
                  4 : "34m",
                  5 : "35m",
                  6 : "36m",
                  7 : "37m",
                  8 : "1;30m",
                  9 : "1;31m",
                 10 : "1;32m",
                 11 : "1;33m",
                 12 : "1;34m",
                 13 : "1;35m",
                 14 : "1;36m",
                 15 : "1;37m"
                  }
    
    colors_bk = { 0 : "40m",
                  1 : "41m",
                  2 : "42m",
                  3 : "43m",
                  4 : "44m",
                  5 : "45m",
                  6 : "46m",
                  7 : "47m",
                  }
    
    def __init__(self):
        self.fg = None
        self.bk = None
        self.havecolor = 1
        self.dotitles = 1
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)

        
    def restore_buffered_mode(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)


    def enable_unbuffered_input_mode(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)
            
    def putch(self, ch):
        sys.stdout.write(ch)

    def getch(self):
        return sys.stdin.read(1)

    def getche(self):
        ch = self.getch()
        self.putch(ch)
        return ch

    def kbhit(self, timeout=0):
        self.print_at(40,1, "WAITING")
        dr,dw,de = select([sys.stdin], [], [], timeout)
        self.print_at(40,1, "DONE   ")
        return dr != []
        
    def no_colors(self):
        self.havecolor = 0    
        
    def set_color(self, fg = None, bk = None):
        if fg != None:
            sys.stdout.write(TerminalANSIPosix.escape + TerminalANSIPosix.colors_fg[fg])
        if bk != None:
            sys.stdout.write(TerminalANSIPosix.escape + TerminalANSIPosix.colors_bk[bk])
        
    def set_title(self, title):
        if "TERM" in os.environ:
            myt=os.environ["TERM"]
            if myt in ["xterm","Eterm","aterm","rxvt", "xterm-color"]:
                sys.stderr.write("\x1b]1;\x07\x1b]2;"+str(title)+"\x07")
                sys.stderr.flush()

    def cprint(self, fg, bk, text):
        self.set_color(fg, bk)
        print (text,end="")
    
    def print_at(self, x, y, text):
            self.gotoXY(x, y)
            print(text,end="")
            
    def clear(self):
        sys.stdout.write(TerminalANSIPosix.codes["clear"])
        
    def gotoXY(self, x,y):
        sys.stdout.write(TerminalANSIPosix.codes["gotoxy"] % (y, x))
    
    def save_pos(self):
        sys.stdout.write(TerminalANSIPosix.codes["save"])
        
    def restore_pos(self):
        sys.stdout.write(TerminalANSIPosix.codes["restore"])
        
    def reset(self):
        sys.stdout.write(TerminalANSIPosix.codes["reset"])
        
    def move_left(self, c = 1):
        sys.stdout.write(TerminalANSIPosix.codes["move_left"] % c)
        
    def move_right(self, c = 1):
        sys.stdout.write(TerminalANSIPosix.codes["move_right"] % c)
        
    def move_up(self, c = 1):
        sys.stdout.write(TerminalANSIPosix.codes["move_up"] % c)
        
    def move_down(self, c = 1):
        sys.stdout.write(TerminalANSIPosix.codes["move_down"] % c)
        
    def columns(self):
        if "COLUMNS" in os.environ:
            return os.environ["COLUMNS"]
        else:
            return 0
    
    def lines(self):
        if "LINES" in os.environ:
            return os.environ["LINES"]
        else:
            return 0


if __name__ == "__main__":
    t = get_terminal()
    t.enable_unbuffered_input_mode()
    t.clear()
    t.gotoXY(0,0)
    t.set_title("Testing output")
    print("            Foreground 111111")
    print("Background   0123456789012345")
    for b in range(8):
        t.reset()
        print("            ",end="")
        print(b,end="")
        for f in range(16):
            t.cprint(f,b, f % 10)
        print()
    a = 0
    b = 0
    t.reset()
    try:
        while(True):
            t.print_at(a , 20 + b % 20, ".")
            if t.kbhit(0.01):
                t.print_at(50, 6, ord(t.getch()))
            t.print_at(40, 5, "%d %d" % (a,b))
            b+=1
            a = b / 20.0 % 20
            t.print_at(40,6, b)
            t.print_at(a , 20 + b % 20, "*")
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    t.clear()
    t.reset()
    t.restore_buffered_mode()

    