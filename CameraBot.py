#!/usr/bin/python

from datetime              import datetime
from subprocess            import *
from time                  import sleep, strftime
from Queue                 import Queue
from threading             import Thread
from MOCK_CharLCDPlate     import MOCK_CharLCDPlate
from CameraBotConfig       import CameraBotConfig 

try:
   import smbus
   from Adafruit_I2C          import Adafruit_I2C
   from Adafruit_MCP230xx     import Adafruit_MCP230XX
   from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
except ImportError:
   print("Import Errors must be testing")

# initialize the LCD plate
#   use busnum = 0 for raspi version 1 (256MB) 
#   and busnum = 1 for raspi version 2 (512MB)
LCD = Adafruit_CharLCDPlate(busnum = 0)
#LCD = MOCK_CharLCDPlate(busnum = 0)

# Define a queue to communicate with worker thread
LCD_QUEUE = Queue()

CONFIG = CameraBotConfig()

SHOT_COUNT = 0

ON_MAIN_SCREEN = True

# Buttons
NONE           = 0x00
SELECT         = 0x01
RIGHT          = 0x02
DOWN           = 0x04
UP             = 0x08
LEFT           = 0x10
UP_AND_DOWN    = 0x0C
LEFT_AND_RIGHT = 0x12

DELAY_VALUES = [.5,1,2,3,4,5,6,7,8,9,10,15,20,30,40,50,60,90,120,150,300,600,1200,3600]
MODE_TYPES = ['TL','ST','TLS']
CAMERA_TYPES = ['INT','EXT']
RESOLUTION_LIST = ['1MP','2MP','3MP','4MP','5MP']
IMAGE_QUALITY_VALUES = [10,20,30,40,50,60,70,80,90,100]

# ----------------------------
# WORKER THREAD
# ----------------------------

# Define a function to run in the worker thread
def update_lcd(q):
   
   while True:
      msg = q.get()
      # if we're falling behind, skip some LCD updates
      while not q.empty():
         q.task_done()
         msg = q.get()
      LCD.clear()
      LCD.setCursor(0,0)
      LCD.message(msg)
      q.task_done()
   return


def runCameraCommands(outputFolder):
   global SHOT_COUNT
   global ON_MAIN_SCREEN
   while True:
      print('dest folder=' + outputFolder + '\r')
      SHOT_COUNT += 1
      if (ON_MAIN_SCREEN):
         display_main_screen()
      
      sleep(DELAY_VALUES[CONFIG.tlDelayIdx])
   
   return

def generateCameraCmdFromConfig():
   return 'some command'


# ----------------------------
# MAIN LOOP
# ----------------------------

def main():

   # Setup AdaFruit LCD Plate
   LCD.begin(16,2)
   LCD.clear()
   LCD.backlight(LCD.ON)

   # read CFG and assign the values to global vars
   CONFIG.tlDelayIdx = 10
   CONFIG.modeIdx = 0
   CONFIG.cameraIdx = 0
   CONFIG.resolutionIdx = 4
   CONFIG.imgQuality = 100

   # Create the worker thread and make it a daemon
   lcd_worker = Thread(target=update_lcd, args=(LCD_QUEUE,))
   lcd_worker.setDaemon(True)
   lcd_worker.start()
   # Display startup banner
   LCD_QUEUE.put('CameraBot\nver. 0.1', True)
   sleep(1)

   #setup the folder to store the images date based???

   #put the camera worker thread here
   camera_worker = Thread(target=runCameraCommands, args=('someFolder',))
   camera_worker.setDaemon(True)
   camera_worker.start()

   display_main_screen()

   continue_main_loop = True
   backlight_counter = 0

   # Main loop
   while continue_main_loop:
      press = read_buttons()

      backlight_counter += 1
      if (backlight_counter > 300):#30 seconds
         LCD.backlight(LCD.OFF)
      
      if (press != NONE):
         backlight_counter = 0 
         LCD.backlight(LCD.ON)

      # LEFT button pressed
      if(press == RIGHT):
         LCD_QUEUE.put("Camera Start", True)
         sleep(1)
         display_main_screen()

      # RIGHT button pressed
      if(press == LEFT):
         LCD_QUEUE.put("Camera Stop", True)
         sleep(1)
         display_main_screen()

      # UP button pressed
      if(press == UP):
         CONFIG.tlDelayIdx = increaseDelay(CONFIG.tlDelayIdx)
         display_main_screen()

      # DOWN button pressed
      if(press == DOWN):
         CONFIG.tlDelayIdx = decreaseDelay(CONFIG.tlDelayIdx)
         display_main_screen()

      # SELECT button pressed
      if(press == SELECT):
         display_main_menu()
         display_main_screen()

      delay_milliseconds(99)
   
   update_lcd.join()#join threads
   runCameraCommands.join()

def display_main_menu():
   display_menu([
      {'text':'TL Delay (s)', 'idxAttr':'tlDelayIdx', 'values':DELAY_VALUES},
      {'text':'Operation Mode', 'idxAttr':'modeIdx', 'values':MODE_TYPES},
      {'text':'Select Camera', 'idxAttr':'cameraIdx', 'values':CAMERA_TYPES},
      {'text':'Resolution', 'idxAttr':'resolutionIdx', 'values':RESOLUTION_LIST}
      ])

def display_menu(menuItems):
   global ON_MAIN_SCREEN
   ON_MAIN_SCREEN = False
   curMenuIdx = 0
   display_menu_item(menuItems[curMenuIdx])
   keep_looping = True
   while keep_looping:
      buttons = read_buttons()
      curIdxAttrName = menuItems[curMenuIdx]['idxAttr']

      if (buttons == UP):
         if (curMenuIdx > 0):
            curMenuIdx -= 1
         else:
            curMenuIdx = len(menuItems) - 1
         display_menu_item(menuItems[curMenuIdx])
      
      if (buttons == DOWN):
         if (curMenuIdx >= len(menuItems)-1):
            curMenuIdx = 0
         else:
            curMenuIdx += 1
         display_menu_item(menuItems[curMenuIdx])

      if (buttons == LEFT):
         if (getattr(CONFIG, curIdxAttrName) > 0):
            setattr(CONFIG, curIdxAttrName, getattr(CONFIG, curIdxAttrName) - 1)
         else:
            setattr(CONFIG, curIdxAttrName, len(menuItems[curMenuIdx]['values'])-1)
         display_menu_item(menuItems[curMenuIdx])
      
      if (buttons == RIGHT):
         if (getattr(CONFIG, curIdxAttrName) >= len(menuItems[curMenuIdx]['values'])-1):
            setattr(CONFIG, curIdxAttrName, 0)
         else:
            setattr(CONFIG, curIdxAttrName, getattr(CONFIG, curIdxAttrName) + 1)
         display_menu_item(menuItems[curMenuIdx])

      if (buttons == SELECT):
         keep_looping = False
      #end of main menu loop
   display_main_screen();

def display_menu_item(menuItem):
   LCD_QUEUE.put(menuItem['text'] + 
      "\nCurrent: " + str(menuItem['values'][getattr(CONFIG,menuItem['idxAttr'])]))

def display_main_screen():
   global SHOT_COUNT
   global ON_MAIN_SCREEN
   ON_MAIN_SCREEN = True
   diskUsage = run_cmd("df -h / |grep -m1 -o ' [0-9]*% '|head -1")
   LCD_QUEUE.put("du:" + diskUsage[:4] + "  " + 
      MODE_TYPES[CONFIG.modeIdx] + "-" + CAMERA_TYPES[CONFIG.cameraIdx] +
      "\n#" + str(SHOT_COUNT).zfill(4) + "     " + 
      str(DELAY_VALUES[CONFIG.tlDelayIdx]) + "s", True)

# ----------------------------
# READ SWITCHES
# ----------------------------

def read_buttons():

   buttons = LCD.buttons()
   # Debounce push buttons
   if(buttons != 0):
      while(LCD.buttons() != 0):
         delay_milliseconds(1)
   return buttons



def delay_milliseconds(milliseconds):
   seconds = milliseconds / float(1000) # divide milliseconds by 1000 for seconds
   sleep(seconds)



def increaseDelay(curDelayIdx):
   if curDelayIdx < len(DELAY_VALUES) - 2:
      delayIdx = curDelayIdx + 1
      return delayIdx
   else:
      return curDelayIdx

def decreaseDelay(curDelayIdx):
   if curDelayIdx > 0:
      delayIdx = curDelayIdx - 1
      return delayIdx
   else:
      return curDelayIdx

# ----------------------------

def run_cmd(cmd):
   p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
   output = p.communicate()[0]
   return output



#def run_cmd_nowait(cmd):
#   pid = Popen(cmd, shell=True, stdout=NONE, stderr=STDOUT).pid


if __name__ == '__main__':
  main()
