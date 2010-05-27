#
# ColorConsole
#
# Inspired/copied/adapted from:
# 
# output.py from Gentoo and 
# http://code.activestate.com/recipes/572182-how-to-implement-kbhit-on-linux/ and
# http://www.burgaud.com/bring-colors-to-the-windows-console-with-python/
#
#

# Added for Python 2.6 compatibility
from __future__ import print_function
import os,sys

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
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    WAIT_TIMEOUT = 0x00000102
    WAIT_OBJECT_0 = 0
    
    def __init__(self):
        self.fg = None
        self.bk = None
        self.havecolor = 1
        self.dotitles = 1
        self.stdout_handle = windll.kernel32.GetStdHandle(TerminalWindows.STD_OUTPUT_HANDLE)
        self.stdin_handle = windll.kernel32.GetStdHandle(TerminalWindows.STD_INPUT_HANDLE)
        self.reset_attrib = self.__get_text_attr()
        self.savedX = 0
        self.savedY = 0
       
    def restore_buffered_mode(self):
        self.__set_text_attr(self.reset_attrib)

    def enable_unbuffered_input_mode(self):
        pass

    def putch(self, ch):
        msvcrt.putc(ch)

    def getch(self):
        return msvcrt.getch()
        #n = DWORD(1)
        #out = DWORD(0)
        #buff = ctypes.create_string_buffer(4)
        #ReadConsoleA(self.stdin_handle, buff, n, byref(out), None)
        #print(buff[0])
        #print(out)
        #return buff[0] 

    def getche(self):
        return msvcrt.getche()

    def kbhit(self, timeout=0): # Ignores timeout... should be slown down
        #t = DWORD(int(timeout*1000))
        #t = timeout 
        #return WaitForSingleObject(TerminalWindows.STD_INPUT_HANDLE, t) == TerminalWindows.WAIT_OBJECT_0 
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
        
    def __get_console_info(self):
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        GetConsoleScreenBufferInfo(self.stdout_handle, byref(csbi))
        return csbi
        
    def __get_text_attr(self):
          return self.__get_console_info().wAttributes

    def __set_text_attr(self, color):
          sys.stdout.flush()
          SetConsoleTextAttribute(self.stdout_handle, color)

    def set_title(self, title):
        ctitle = c_char_p(title)
        SetConsoleTitle(ctitle)

    def cprint(self, fg, bk, text):
        self.set_color(fg, bk)
        print (text,end="")
        sys.stdout.flush()

    def print_at(self, x, y, text):
            self.gotoXY(x, y)
            print(text,end="")
            sys.stdout.flush()

    def clear(self):              # From kb q99261
        rp = COORD()
        wr = DWORD()
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        GetConsoleScreenBufferInfo(self.stdout_handle, byref(csbi))
        sx = csbi.dwSize.X * csbi.dwSize.Y
        
        FillConsoleOutputCharacter( self.stdout_handle, 0,
                                    sx, rp, byref(wr))
        FillConsoleOutputAttribute( self.stdout_handle, csbi.wAttributes,
                                    sx, rp, byref(wr) );                                        

    def gotoXY(self, x,y):
        p = COORD()
        p.X = int(x)
        p.Y = int(y)
        SetConsoleCursorPosition(self.stdout_handle, p)
        pass

    def save_pos(self):
        csbi = __get_console_info()
        self.savedX = csbi.dwCursorPosition.X
        self.savedY = csbi.dwCursorPosition.Y
        pass

    def restore_pos(self):
        self.gotoXY(self.savedX, self.savedY)

    def reset(self):
        self.__set_text_attr(self.reset_attrib)
        
    def __move_from(self, dx, dy):
        csbi = self.__get_console_info()
        ax = csbi.dwCursorPosition.X
        ay = csbi.dwCursorPosition.Y
        self.gotoXY(ax+dx, ay+dy)
        

    def move_left(self, c = 1):
        self.__move_from(-c,0)

    def move_right(self, c = 1):
        self.__move_from(c,0)

    def move_up(self, c = 1):
        self.__move_from(0,-c)

    def move_down(self, c = 1):
        self.__move_from(0,c)

    def columns(self):
        csbi = self.__get_console_info()
        return csbi.dwSize.X
        
    def lines(self):
        csbi = self.__get_console_info()
        return csbi.dwSize.Y



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



if os.name == "nt":
        import msvcrt
        import ctypes
        from ctypes import windll, Structure, c_short, c_ushort, byref, c_char_p, c_uint
        SHORT = c_short
        WORD = c_ushort
        DWORD = c_uint

        class COORD(Structure):
          """struct in wincon.h."""
          _fields_ = [
            ("X", SHORT),
            ("Y", SHORT)]

        class SMALL_RECT(Structure):
          """struct in wincon.h."""
          _fields_ = [
            ("Left", SHORT),
            ("Top", SHORT),
            ("Right", SHORT),
            ("Bottom", SHORT)]

        class CONSOLE_SCREEN_BUFFER_INFO(Structure):
          """struct in wincon.h."""
          _fields_ = [
            ("dwSize", COORD),
            ("dwCursorPosition", COORD),
            ("wAttributes", WORD),
            ("srWindow", SMALL_RECT),
            ("dwMaximumWindowSize", COORD)]
        SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
        GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo
        SetConsoleTitle = windll.kernel32.SetConsoleTitleA
        GetConsoleTitle = windll.kernel32.GetConsoleTitleA
        SetConsoleCursorPosition = windll.kernel32.SetConsoleCursorPosition
        FillConsoleOutputCharacter = windll.kernel32.FillConsoleOutputCharacterA
        FillConsoleOutputAttribute = windll.kernel32.FillConsoleOutputAttribute
        WaitForSingleObject = windll.kernel32.WaitForSingleObject
        ReadConsoleA = windll.kernel32.ReadConsoleA

if os.name == "posix":
  import termios
  from select import select   




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

    
