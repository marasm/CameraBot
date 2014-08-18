#!/usr/bin/python

from datetime              import datetime
from subprocess            import *
from time                  import sleep, strftime
from Queue                 import Queue
from threading             import Thread
from MOCK_CharLCDPlate     import MOCK_CharLCDPlate

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
#LCD = Adafruit_CharLCDPlate(busnum = 0)
LCD = MOCK_CharLCDPlate(busnum = 0)

# Define a queue to communicate with worker thread
LCD_QUEUE = Queue()


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



# ----------------------------
# MAIN LOOP
# ----------------------------

def main():

   # Setup AdaFruit LCD Plate
   LCD.begin(16,2)
   LCD.clear()
   LCD.backlight(LCD.ON)

   # read CFG and assign the values to global vars
   shotCount = 0
   mode = "TL-INT" #will need to read from config
   delayIdx = 10 #Will need to read from config

   # Create the worker thread and make it a daemon
   lcd_worker = Thread(target=update_lcd, args=(LCD_QUEUE,))
   lcd_worker.setDaemon(True)
   lcd_worker.start()
   # Display startup banner
   LCD_QUEUE.put('CameraBot\nver. 0.1', True)
   sleep(2)

   #put the camera worker thread here


   display_main_screen(mode, shotCount, delayIdx)

   # Main loop
   while True:
      press = read_buttons()

      # LEFT button pressed
      if(press == LEFT):
         LCD_QUEUE.put("Timelapse Start", True)

      # RIGHT button pressed
      if(press == RIGHT):
         LCD_QUEUE.put("Timelapse Stop", True)

      # UP button pressed
      if(press == UP):
         delayIdx = increaseDelay(delayIdx)

      # DOWN button pressed
      if(press == DOWN):
         delayIdx = decreaseDelay(delayIdx)

      # SELECT button pressed
      if(press == SELECT):
         menu_pressed()

      display_main_screen(mode, shotCount, delayIdx)
      delay_milliseconds(99)
   
   update_lcd.join()#join threads


def display_main_screen(mode, shotCount, delayIdx):
   diskUsage = run_cmd("df -h / |grep -m1 -o ' [0-9]*% '|head -1")
   LCD_QUEUE.put("du:" + diskUsage[:4] + "  " + mode + 
      "\n#" + str(shotCount).zfill(4) + "     " + str(DELAY_VALUES[delayIdx]) + "s", True)

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


# ----------------------------
# RADIO SETUP MENU
# ----------------------------

def menu_pressed():

   MENU_LIST = [
      '1. Display Time \n   & IP Address ',
      '2. Output Audio \n   to HDMI      ',
      '3. Output Audio \n   to Headphones',
      '4. Auto Select  \n   Audio Output ',
      '5. Reload       \n   Playlist File',
      '6. System       \n   Shutdown!    ',
      '7. Back         \n                ']

   item = 0
   LCD_QUEUE.put(MENU_LIST[item], True)

   keep_looping = True
   while (keep_looping):

      # Wait for a key press
      press = read_buttons()

      # UP button
      if(press == UP):
         item -= 1
         if(item < 0):
            item = len(MENU_LIST) - 1
         LCD_QUEUE.put(MENU_LIST[item], True)

      # DOWN button
      elif(press == DOWN):
         item += 1
         if(item >= len(MENU_LIST)):
            item = 0
         LCD_QUEUE.put(MENU_LIST[item], True)

      # SELECT button = exit
      elif(press == SELECT):
         keep_looping = False

         # Take action
         if(  item == 0):
            # 1. display time and IP address
            display_ipaddr()
         elif(item == 1):
            # 2. audio output to HDMI
            output = run_cmd("amixer -q cset numid=3 2")
         elif(item == 2):
            # 3. audio output to headphone jack
            output = run_cmd("amixer -q cset numid=3 1")
         elif(item == 3):
            # 4. audio output auto-select
            output = run_cmd("amixer -q cset numid=3 0")
         elif(item == 4):
            # 5. reload our station playlist
            LCD_QUEUE.put("Reloading\nPlaylist File...", True)
         elif(item == 5):
            # 6. shutdown the system
            LCD_QUEUE.put('Shutting down\nLinux now! ...  ', True)
            LCD_QUEUE.join()
            output = run_cmd("sudo shutdown now")
            LCD.clear()
            LCD.backlight(LCD.OFF)
            exit(0)
      else:
         delay_milliseconds(99)

   # Restore display
   display_main_screen()



# ----------------------------
# DISPLAY TIME AND IP ADDRESS
# ----------------------------

def display_ipaddr():
   show_wlan0 = "ip addr show wlan0 | cut -d/ -f1 | awk '/inet/ {printf \"w%15.15s\", $2}'"
   show_eth0  = "ip addr show eth0  | cut -d/ -f1 | awk '/inet/ {printf \"e%15.15s\", $2}'"
   eipaddr = run_cmd(show_eth0)
   wipaddr = run_cmd(show_wlan0)

   i = 29
   keep_looping = True
   while (keep_looping):

      # Every 1/2 second, update the time display
      i += 1
      #if(i % 10 == 0):
      # Every 3 seconds, update ethernet or wi-fi IP address
      if(i == 60):
         eipaddr = run_cmd(show_eth0)
         wipaddr = run_cmd(show_wlan0)
         i = 0

      if(i % 5 == 0):
         LCD_QUEUE.put(eipaddr + wipaddr, True)

      # Every 100 milliseconds, read the switches
      press = read_buttons()
      # Take action on switch press
      
      # SELECT button = exit
      if(press == SELECT):
         keep_looping = False
         
      delay_milliseconds(99)

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
