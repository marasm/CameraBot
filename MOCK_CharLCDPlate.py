#!/usr/bin/python


from time import sleep

class _Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): 
        char = self.impl()
        if char == '\x03':
            raise KeyboardInterrupt
        elif char == '\x04':
            raise EOFError
        return char

class _GetchUnix:
    def __init__(self):
        import tty
        import sys

    def __call__(self):
        import sys
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

getch = _Getch()


class MOCK_CharLCDPlate():

    # ----------------------------------------------------------------------
    # Constants

    # Port expander registers
    MCP23017_IOCON_BANK0    = 0x0A  # IOCON when Bank 0 active
    MCP23017_IOCON_BANK1    = 0x15  # IOCON when Bank 1 active
    # These are register addresses when in Bank 1 only:
    MCP23017_GPIOA          = 0x09
    MCP23017_IODIRB         = 0x10
    MCP23017_GPIOB          = 0x19


    NONE           = 0x00
    SELECT         = 0x01
    RIGHT          = 0x02
    DOWN           = 0x04
    UP             = 0x08
    LEFT           = 0x10

    # LED colors
    OFF                     = 0x00
    RED                     = 0x01
    GREEN                   = 0x02
    BLUE                    = 0x04
    YELLOW                  = RED + GREEN
    TEAL                    = GREEN + BLUE
    VIOLET                  = RED + BLUE
    WHITE                   = RED + GREEN + BLUE
    ON                      = RED + GREEN + BLUE

    # LCD Commands
    LCD_CLEARDISPLAY        = 0x01
    LCD_RETURNHOME          = 0x02
    LCD_ENTRYMODESET        = 0x04
    LCD_DISPLAYCONTROL      = 0x08
    LCD_CURSORSHIFT         = 0x10
    LCD_FUNCTIONSET         = 0x20
    LCD_SETCGRAMADDR        = 0x40
    LCD_SETDDRAMADDR        = 0x80

    # Flags for display on/off control
    LCD_DISPLAYON           = 0x04
    LCD_DISPLAYOFF          = 0x00
    LCD_CURSORON            = 0x02
    LCD_CURSOROFF           = 0x00
    LCD_BLINKON             = 0x01
    LCD_BLINKOFF            = 0x00

    # Flags for display entry mode
    LCD_ENTRYRIGHT          = 0x00
    LCD_ENTRYLEFT           = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # Flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE  = 0x00
    LCD_MOVERIGHT   = 0x04
    LCD_MOVELEFT    = 0x00

    # Line addresses for up to 4 line displays.  Maps line number to DDRAM address for line.
    LINE_ADDRESSES = { 1: 0xC0, 2: 0x94, 3: 0xD4 }

    # Truncation constants for message function truncate parameter.
    NO_TRUNCATE       = 0
    TRUNCATE          = 1
    TRUNCATE_ELLIPSIS = 2

    # ----------------------------------------------------------------------
    # Constructor

    def __init__(self, busnum=-1, addr=0x20, debug=False, backlight=ON):
        print("Init I2c busnum={0}".format(busnum))
        

    def clear(self):
        self.message("",True)


    def home(self):
        self.message("", True)

    def begin(self, cols, lines):
        self.currline = 0
        self.numlines = lines
        self.numcols = cols
        self.buttonsDebounced = True
        self.clear()
        print("Begin\r")

    def setCursor(self, col, row):
        if row > self.numlines: row = self.numlines - 1
        elif row < 0:           row = 0
        print("Set cursor at {0},{1}\r".format(col,row))


    def display(self):
        """ Turn the display on (quickly) """
        self.displaycontrol |= self.LCD_DISPLAYON
        print("Display ON\r")


    def noDisplay(self):
        """ Turn the display off (quickly) """
        self.displaycontrol &= ~self.LCD_DISPLAYON
        print("Display OFF\r")


    def cursor(self):
        """ Underline cursor on """
        self.displaycontrol |= self.LCD_CURSORON
        print("Cursor ON\r")


    def noCursor(self):
        """ Underline cursor off """
        self.displaycontrol &= ~self.LCD_CURSORON
        print("Cursor OFF\r")


    def ToggleCursor(self):
        """ Toggles the underline cursor On/Off """
        self.displaycontrol ^= self.LCD_CURSORON
        print("Cursor Toggle\r")


    def blink(self):
        """ Turn on the blinking cursor """
        self.displaycontrol |= self.LCD_BLINKON
        print("Cursor Blink ON\r")


    def noBlink(self):
        """ Turn off the blinking cursor """
        self.displaycontrol &= ~self.LCD_BLINKON
        print("Cursor Blink ON\r")


    def ToggleBlink(self):
        """ Toggles the blinking cursor """
        self.displaycontrol ^= self.LCD_BLINKON
        print("Cursor Blink Toggle\r")


    def scrollDisplayLeft(self):
        """ These commands scroll the display without changing the RAM """
        self.displayshift = self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT
        print("Display scroll LEFT\r")


    def scrollDisplayRight(self):
        """ These commands scroll the display without changing the RAM """
        self.displayshift = self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT
        print("Display scroll RIGHT\r")


    def leftToRight(self):
        """ This is for text that flows left to right """
        self.displaymode |= self.LCD_ENTRYLEFT
        print("Text flow Left to Right\r")


    def rightToLeft(self):
        """ This is for text that flows right to left """
        self.displaymode &= ~self.LCD_ENTRYLEFT
        print("Text flow Right to Left\r")


    def autoscroll(self):
        """ This will 'right justify' text from the cursor """
        self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
        print("Text right justify\r")

    def noAutoscroll(self):
        """ This will 'left justify' text from the cursor """
        self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
        print("Text left justify\r")


    def createChar(self, location, bitmap):
        print("Create char {0} at location {1}\r".format(bitmap,location))


    def message(self, text, truncate=NO_TRUNCATE):
        """ Send string to LCD. Newline wraps to second line"""
        if not text: 
            lines = ['                ','                ']
        lines = str(text).split('\n', 1)
        if (len(lines) == 1):
            lines.append('                ')

        print("+----------------+\r")
        for i, line in enumerate(lines):
            linelen = len(line)
            if truncate == self.TRUNCATE and linelen > self.numcols:
                # Hard truncation of line.
                print("|{0}|\r".format(line[0:self.numcols]))
            elif truncate == self.TRUNCATE_ELLIPSIS and linelen > self.numcols:
                # Nicer truncation with ellipses.
                print("|{0}|\r".format(line[0:self.numcols-3] + '...'))
            else:
                print(str("|{0}|\r".format(line.ljust(self.numcols))))
        print("+----------------+\r")



    def backlight(self, color):
        print("LCD Backlight {0}\r".format(color))

    # Read state of single button
    def buttonPressed(self, b):
        return b == self.decodeRegToGPIOButton(getch())


    # Read and return bitmask of combined button state
    def buttons(self):
        if self.buttonsDebounced:
            self.buttonsDebounced = False
            return self.decodeRegToGPIOButton(getch())
        else:
            self.buttonsDebounced = True
            return self.NONE


    def decodeRegToGPIOButton(self, button):
        if button == 'a':
            return self.LEFT
        elif button == 'd':
            return self.RIGHT
        elif button == 'w':
            return self.UP
        elif button == 's':
            return self.DOWN
        elif button == '\r':
            return self.SELECT
        else:
            return self.NONE

        


if __name__ == '__main__':

    lcd = MOCK_CharLCDPlate()
    lcd.begin(16, 2)
    lcd.clear()
    lcd.message("Adafruit RGB LCD\nPlate w/Keypad!")
    sleep(5)


