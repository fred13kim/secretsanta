#!/usr/bin/python3
import time
import board
import neopixel
import random
import signal
import sys
import RPi.GPIO as GPIO
import numpy as np

button_gpio = 2
pixel_pin = board.D18
num_pixels = 60
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.75, auto_write=False, pixel_order=ORDER
    )

width = 6
height = 10
raindrop_start = -9
raindrop_initalspeed = 0.005
index_list = np.reshape(list(range(width*height)),(width,height))
temp1_list = index_list[::2]
temp2_list = np.fliplr(index_list[1::2])
index_list[::2] = temp1_list
index_list[1::2] = temp2_list
index_list = np.reshape(index_list,width*height)

#rainfall is 0 static is 1 off is 2
event_state = 0

def handler(sig,frame):
    GPIO.cleanup()
    sys.exit(0)
def callback(channel):
    global event_state
    event_state = (event_state + 1) % 7

class Drop:
    def __init__(self):
        self.x = random.randint(0,width-1)
        self.y = random.randint(raindrop_start,0)
        self.yspeed = random.randint(1,5) * 0.005
        (self.r, self.g, self.b) = (0,255,0)
        self.tail = 10
    def fall(self):
        self.y = self.y + self.yspeed
        self.yspeed = self.yspeed + 0.00001
        if int(self.y) > height + self.tail - 1:
            self.x = random.randint(0,width-1)
            self.y = random.randint(raindrop_start,0)
            self.yspeed = random.randint(1,5) * 0.005
            (self.r, self.g, self.b) = (random.randint(200,255),random.randint(200,255),0)
    def show(self):
        for i in range(self.tail):
            j = int(self.y) - i
            if j >= 0 and j < height:
                idx = int(j) + self.x * height
                r = int(((self.r/self.tail) * (self.tail - i)))
                g = int(((self.g/self.tail) * (self.tail - i)))
                b = int(((self.b/self.tail) * (self.tail - i)))
                pixels[index_list[idx]] = (r,g,b)


drops = []
def rain_setup():
    for i in range(10):
        drops.append(Drop())
def rain_draw():
    for drop in drops:
        drop.fall()
        drop.show()
    pixels.show()
def hex_to_rgb(hex):
  return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
static_cond = 0
matrix = [['00ff00','00ff00','00ff00','00ff00','00ff00','00ff00'],
          ['00ff00','00ff00','a3ec9e','a3ec9e','00ff00','00ff00'],
          ['00ff00','00ff00','e7c6b7','e7c6b7','00ff00','00ff00'],
          ['00ff00','ffff00','e7c6b7','e7c6b7','00ff00','00ff00'],
          ['00ff00','00ff00','e7f7f7','e7c6b7','00ff00','00ff00'],
          ['00ff00','00ff00','e7f7f7','e7f7f7','e7f7f7','00ff00'],
          ['00ff00','00ff00','e7f7f7','e7f7f7','e7f7f7','00ff00'],
          ['00ff00','e7c6b7','e7f7f7','e7f7f7','e7f7f7','00ff00'],
          ['e7c6b7','e7c6b7','e7f7f7','e7f7f7','e7f7f7','00ff00'],
          ['e7c6b7','e7c6b7','e7f7f7','e7f7f7','e7f7f7','00ff00'],
          ]

def main():
    rain_setup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(button_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(button_gpio,GPIO.FALLING,callback=callback,bouncetime=200)
    signal.signal(signal.SIGINT, handler)
    try:
        while (True):
            if (event_state == 0):
                static_cond = 0
                rain_draw()
            elif (event_state == 1 and static_cond == 0):
                for i in range(255):
                    pixels.fill((0,i,0))
                    pixels.show()
                static_cond = 1
            elif (event_state == 2):
                i = 0
                while (i < 255):
                    pixels.fill((0,int(i),0))
                    pixels.show()
                    i = i + 0.5
                while (i > 0):
                    pixels.fill((0,int(i),0))
                    pixels.show()
                    i = i - 0.5
            elif (event_state == 5 and static_cond == 1):
                for i in range(85):
                    pixels.fill((i,i,i))
                    pixels.show()
                static_cond = 2
            elif (event_state == 4):
                r = 0
                c = 0
                for r in range(len(matrix)):
                    for c in range(len(matrix[r])):
                        pixels[index_list[r + c*len(matrix)]] = hex_to_rgb(matrix[r][c])
                        c=c+1
                    r=r+1
                pixels.show()
            elif (event_state == 3):
                while (i < 85):
                    pixels.fill((int(i),int(i),int(i)))
                    pixels.show()
                    i = i + 0.15
                while (i > 0):
                    pixels.fill((int(i),int(i),int(i)))
                    pixels.show()
                    i = i - 0.15
            elif (event_state == 6 and static_cond == 2):
                for i in range(85):
                    pixels.fill((85-i,85-i,85-i))
                    pixels.show()
                static_cond = 3
    finally:
        pixels.fill((0,0,0))
        pixels.show()


if __name__ == "__main__":
    main()
