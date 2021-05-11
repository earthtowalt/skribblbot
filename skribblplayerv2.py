'''Automated skribbl player'''

import os, sys
import time
import random
import cv2

import pyautogui as pg
import tkinter as tk 
import numpy as np

from svgtrace import trace
from google_images_download import google_images_download 

# cd to the file directory
os.chdir(os.path.dirname(__file__))

# create global corners variable
# accessed by the tk mainloop and by the image warp code
corners = [None, None]

def getcoords():
    # state variables
    global corners
    corners = [None, None] # global will be used to store the click position

    # event handling function
    def handle(event):
        global corners
        print("click detected")
        # collect click at correct index if necessary
        if corners[0] == None:
            corners[0] = (event.x,event.y)
        elif corners[1] == None:
            corners[1] = (event.x,event.y)
            
        # after clicks collected destroy window
        if None not in corners:
            root.destroy()
    
    # create a tk overlay to get canvas coords
    root = tk.Tk()
    root.bind("<Button 1>", handle)
    root.attributes('-alpha', 0.3)
    root.state('zoomed')
    root.mainloop()
    
    return corners

# ask for word
word = pg.prompt('Enter word: ')
print(word)
if not word:
    print('invalid word, exiting')
    sys.exit(0)

# google search to get image of word 
response = google_images_download.googleimagesdownload() 
args = {'keywords':word,'limit':1,'print_urls':True}
paths = response.download(args)
# print(paths)

# get canvas corners
corners = getcoords()
print("\ncorners:")
print(corners)

# get important dimensions
canvaswidth = corners[1][0]-corners[0][0]
canvasheight = corners[1][1]-corners[0][1]

# load one of the images downloaded
downloadpath = os.path.join(os.path.dirname(__file__),'downloads',word)
# imagename = random.choice(os.listdir(downloadpath))
imagename = os.listdir(downloadpath)[1]

imagepath = os.path.join(downloadpath,imagename)
# print(imagepath)
image = cv2.imread(imagepath)
# print(image)

# simple resize
image = cv2.resize(image, dsize=(canvaswidth, canvasheight), interpolation=cv2.INTER_CUBIC)

# blur the image 
image = cv2.blur(image, (5,5))

cv2.imshow("blurred", image)

# convert image to binary
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
edged = cv2.Canny(image, 30, 200)
cv2.imshow("Edged", edged)
cv2.waitKey(0)

# find contours? not really sure if this does anything?
# contours, heirarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

# use svgtrace to write an svg file to disk? 
print(trace("imagepath"))


sys.exit(0);


# Any duration less than this is rounded to 0.0 to instantly move the mouse.
pg.MINIMUM_DURATION = 0  # Default: 0.1
# Minimal number of seconds to sleep between mouse moves.
pg.MINIMUM_SLEEP = .005  # Default: 0.05
# The number of seconds to pause after EVERY public function call.
pg.PAUSE = 0  # Default: 0.1

# loop through each pixel in the image, if it is black, click at that position
pg.moveTo(corners[0][0], corners[0][1])
pg.pause=0.01
for row in range(image.shape[0]):
    for col in range(image.shape[1]):
        if image[row][col]:
            pg.moveTo(corners[0][0]+col*step,\
                      corners[0][1]+row*step)
            pg.click()
            