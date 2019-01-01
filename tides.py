import BlynkLib
import time,sys
import grovepi
import subprocess
from wia import Wia



BLYNK_AUTH = 'ecbc16f841e9414c9b970799e14cd012'

# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)

wia = Wia()
wia.access_token = "d_sk_1uTIyfELH72Snu1VrAfVkFNB"


#Names of device owners
names = ["Niall","Colin","Conor","Carla","Bolm","Lorcan","Faye"]

# MAC addresses of devices
macs = ["24:a4:3c:a2:b2:23","ec:10:7b:8e:44:14","38:2d:e8:bc:78:3a","40:b4:cd:98:a0:3b","10:f0:05:27:f0:ba","f4:c2:48:71:78:72","24:a4:3c:a2:b2:23"]


# to register virtual pins first define a handler
@blynk.VIRTUAL_WRITE(1)
def v1_write_handler(value):
    if value: # is the the button is pressed?
        arp_scan()


#arpscan
def arp_scan():
        output = subprocess.check_output("sudo arp-scan -l", shell=True)
        for i in range(len(names)):
                if macs[i] in output:
                        print(names[i] + "'s device is present")
                        wia.Event.publish(name="presence", data=(names[i] + " is in Tides"))
                else:
                        print(names[i] + "'s device is NOT present")
                        wia.Event.publish(name="presence", data=(names[i] + " is not in Tides"))



buzzer = 8

# to register virtual pins first define a handler
@blynk.VIRTUAL_WRITE(2)
def v2_write_handler(value):
        if value: # is the the button is pressed?
                buzzerpy()
                #os.system('python ldc.py')

#buzzerpy
def buzzerpy():
        # Buzz for 1 second
        grovepi.digitalWrite(buzzer,1)
        print ('start')
        time.sleep(1)
if sys.platform == 'uwp':
    import winrt_smbus as smbus
    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
# this device has two I2C addresses
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e

# set backlight to (R,G,B) (values from 0..255 for each)
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)

# send command to display (no need for external use)
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)

# set display text \n for second line(or auto wrap)
def setText(text):
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

#Update the display without erasing the display
def setText_norefresh(text):
    textCommand(0x02) # return home
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    while len(text) < 32: #clears the rest of the screen
        text += ' '
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))



# Register virtual pin handler
@blynk.VIRTUAL_WRITE(3)
def v3_write_handler(value):
    print('Current slider value: {}'.format(value))


# example code
#if __name__=="__main__":
    setText(value)
    wia.Event.publish(name="order", data=(value))
   # setText("1 pint of Guinnes please, Thanks")
    setRGB(0,255,0)
   # time.sleep(25)
   # setRGB(0,255,0)
   # setText("Thank you")
   # time.sleep(0)

# Start Blynk (this call should never return)
blynk.run()

