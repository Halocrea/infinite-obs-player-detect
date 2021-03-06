from difflib import SequenceMatcher
from PIL import Image, ImageTk
from threading import Thread
from time import time, sleep
import numpy as np
import PySimpleGUI as sg
import cv2 as cv
import os
import easyocr

# requires https://obsproject.com/forum/resources/obs-virtualcam.949/
# (doesn't work with obs default virtual camera)

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# haystack_img = cv.imread('assets/sample.jpg', cv.IMREAD_UNCHANGED)
needle_img = cv.imread('assets/arrow2.jpg', cv.IMREAD_UNCHANGED)
needle_img = cv.resize(needle_img, (0,0), fx=0.5, fy=0.5) 
reader = easyocr.Reader(['en'])

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def check_cam_by_index(i, window, stop):
    last_top_left = 0
    # last_bottom_right = 0
    current_player = ''
    side = ''

    cap = cv.VideoCapture(i)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920//2)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080//2)
    cap.set(cv.CAP_PROP_FPS, 10)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    while True:
        sleep(0.2)
        # Capture frame-by-frame
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        cropu1 = frame[round(65/2):round(270/2),0:round(1920/2)]
        result = cv.matchTemplate(cropu1, needle_img, cv.TM_CCOEFF_NORMED)
        # get the best match position
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        
        threshold = 0.8
        if max_val >= threshold:
            # get dimensions of the needle image
            needle_h = needle_img.shape[0]

            if (max_loc != last_top_left):
                last_top_left = max_loc
                top = last_top_left[1]
                bottom = top + needle_h
                left = last_top_left[0] + round(90/2)
                right = left + round(270/2)
                # last_bottom_right = (right, bottom)
                cropu2 = cropu1[top:bottom, left:right]

                player = current_player
                text = reader.readtext(image = cropu2, detail = 0)
                if text:
                    player = text[0].rstrip()
                if current_player != player and similar(current_player, player) < 0.7:
                    current_player = player
                    if left > round(960/2):
                        side = 'Blue'
                    else:
                        side = 'Red'

                    text = ' ' + side + ' | ' + current_player + ' '
                    with open('player.txt', 'w') as f:
                        f.write(current_player)
                        f.close()
                    with open('side.txt', 'w') as f:
                        f.write(side)
                        f.close()
                    with open('side_and_player.txt', 'w') as f:
                        f.write(text)
                        f.close()
                    window['-TEXT-2'].update('Player:' + text)

        if stop():
            break

    # When everything done, release the capture
    cap.release()

allCams = []
def cam_indexes ():
    index = 0
    arr = []
    i = 10
    global allCams

    while i > 0:
        cap = cv.VideoCapture(index)
        if cap.read()[0]:
            allCams.append(index)
            cap.release()
        index += 1
        i -= 1
    return arr

def cams_thumbnail_placeholders():
    # checks the first 10 indexes.
    arr = []
    global allCams
    for i in allCams:
        arr.append(sg.Image(size=(200, 114), key = '-IMAGE-' + str(i), enable_events = True))

    return arr

def get_webcam_preview(index, window):
    cap = cv.VideoCapture(index)
    ret, frame = cap.read()
    if ret:
        fromArray = Image.fromarray(frame)
        fromArray = fromArray.resize((200, 114), Image.Resampling.LANCZOS)
        image = ImageTk.PhotoImage(image = fromArray, size=(200, 114))
        window['-IMAGE-' + str(index)].update(data = image)
        cap.release()

cam_indexes()
layout = [
    [sg.Text('Click on a thumbnail to select the input camera', key = '-TEXT-1')],
    [sg.Text('Player: Waiting for cam selection', key = '-TEXT-2'), sg.Button('Clear', key = '-BTN-CLEAR-')],
    cams_thumbnail_placeholders()
]

def main():
    sg.ChangeLookAndFeel('black')
    window = sg.Window('Infinite Obs Player Detect', layout, icon = 'assets/favicon.ico', finalize = True)
    watch_thread = None
    stop_current_thread = False

    global allCams
    for i in allCams:
        get_webcam_preview(i, window)

    while True:
        sleep(0.2)
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            if watch_thread is not None:
                stop_current_thread = True
                watch_thread.join()
            break
        elif event.startswith('-IMAGE-'):
            window['-TEXT-1'].update('Cam #' + event[-1] + ' selected')
            window['-TEXT-2'].update('Waiting for detection...')
            if watch_thread is not None:
                stop_current_thread = True
                watch_thread.join()
            watch_thread = Thread(target = check_cam_by_index, args = (int(event[-1]), window, lambda: stop_current_thread))
            stop_current_thread = False
            watch_thread.start()
        elif event == '-BTN-CLEAR-':
            window['-TEXT-2'].update('Waiting for detection...')
            with open('player.txt', 'w') as f:
                f.write('')
            with open('side.txt', 'w') as f:
                f.write('')
            with open('side_and_player.txt', 'w') as f:
                f.write('')
    window.close()

main()
