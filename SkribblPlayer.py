'''Automated skribbl player'''

import os, sys
import time
import random
import cv2

import pyautogui as pg
import tkinter as tk 
import numpy as np

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
args = {'keywords':word,'limit':3,'print_urls':True}
paths = response.download(args)
# print(paths)

# get canvas corners
corners = getcoords()
print("\ncorners:")
print(corners)

# load one of the images downloaded
downloadpath = os.path.join(os.path.dirname(__file__),'downloads',word)
imagename = random.choice(os.listdir(downloadpath))
imagepath = os.path.join(downloadpath,imagename)
# print(imagepath)
image = cv2.imread(imagepath)
# print(image)

# convert image to binary
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_,image = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY)
# cv2.imshow("Binary", image)
# cv2.waitKey(0)


# get important dimensions
canvaswidth = corners[1][0]-corners[0][0]
canvasheight = corners[1][1]-corners[0][1]
ratio = image.shape[0]/image.shape[1] # height/width

'''
# resize and crop the image 
if image.shape[0] < image.shape[1]:
    print('tall image')
    # resize the image so the height matches the canvas height.
    res = cv2.resize(image, dsize=(canvasheight,int(canvasheight/ratio)), interpolation=cv2.INTER_CUBIC)
    start = (image.shape[1]-canvaswidth)//2
    res = res[start:start+canvaswidth,:]
else:
    print('wide image')
    # resize the image so that the width matches the canvas width. 
    res = cv2.resize(image, dsize=(int(canvaswidth*ratio), canvaswidth), interpolation=cv2.INTER_CUBIC)
    print(res.shape)
    start = (image.shape[0]-canvasheight)//2
    res = res[:,start:start+canvasheight]
'''
# simple resize and pixelate
step=3
image = cv2.resize(image, dsize=(canvaswidth//step, canvasheight//step), interpolation=cv2.INTER_CUBIC)

# upscale the image 
# image = cv2.resize(image, dsize=(canvaswidth, canvasheight), interpolation=cv2.INTER_NEAREST)

print(image.shape)
cv2.imshow("Binary Image", image)
cv2.waitKey(0)

# Any duration less than this is rounded to 0.0 to instantly move the mouse.
pg.MINIMUM_DURATION = 0  # Default: 0.1
# Minimal number of seconds to sleep between mouse moves.
pg.MINIMUM_SLEEP = 0  # Default: 0.05
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
            