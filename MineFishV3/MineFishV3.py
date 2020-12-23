#
# Copyright 2020 Nitro. All Rights Reserved.
#
# Developer: Nitro (admin@nitrostudio.dev)
# Date: December 2020
# Blog: https://blog.nitrostudio.dev
# Discord: Nitro#1781
#
# This project is licensed under the GNU Affero General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# https://github.com/Nitro1231/MineFish-V3/blob/main/LICENSE
#

# TODO:
# ✔ Add Preview Mode Method.
# Validate the config file.
# Add update check method.
# Add easy setting setup or auto setting detection function.
# Reorganize and optimize the code.

import sys
import cv2
import time
import imutils
import json
import pyautogui
import configparser
import numpy as np
import pygetwindow as gw

# region Basic Info
# Print basic information.
print(",--.   ,--.,--.               ,------.,--.       ,--.         ,--.   ,--.,----.  \n|   `.'   |`--',--,--,  ,---. |  .---'`--' ,---. |  ,---.      \  `.'  / '.-.  | \n|  |'.'|  |,--.|      \| .-. :|  `--, ,--.(  .-' |  .-.  |      \     /    .' <  \n|  |   |  ||  ||  ||  |\   --.|  |`   |  |.-'  `)|  | |  |       \   /   /'-'  | \n`--'   `--'`--'`--''--' `----'`--'    `--'`----' `--' `--'        `-'    `----'  ")
print(f'{"=" * 10}Info{"=" * 10}')
print('Developer: Nitro')
print('Email: admin@nitrostudio.dev')
print('Blog: http://blog.nitrostudio.dev/')
print('Discord: Nitro#1781\n')
print('Build: 3.0.1\n')
# endregion

# region Config and Initialization
# Read config file.
config = configparser.ConfigParser()
config.read('./config.ini')
textImage = f'./Core/img/{config.get("MineFishV3 Setting", "image").strip()}'
langType = config.get('MineFishV3 Setting', 'language')
delay = float(config.get('MineFishV3 Setting', 'delay'))
accuracy = float(config.get('MineFishV3 Setting', 'accuracy'))
preview = int(config.get('MineFishV3 Setting', 'preview'))

# Read language file.
with open('./Core/Language.json', encoding='utf-8') as f:
    lang = json.load(f)
langData = lang[langType]

# Load a description for preview mode.
if preview == 1:
    previewD = langData["Text17"]
elif preview == 2:
    previewD = langData["Text18"]
else:
    previewD = langData["Text16"]

# Print the current setting.
print(f'{"=" * 10}{langData["Text10"]}{"=" * 10}') # Setting
print(f'{langData["Text11"]}\"{textImage}\"') # Image File: 
print(f'{langData["Text12"]}{langType}') # Language: 
print(f'{langData["Text13"]}{delay}') # Delay: 
print(f'{langData["Text14"]}{accuracy}') # Threshold: 
print(f'{langData["Text15"]}{preview} ({previewD})') # Preview Mode: 

# Load the target image and convert it into grayscale.
target = cv2.imread(textImage)
target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

vaild = True

print()
print(langData['Text1']) # [Info] Initialized completed.
# endregion

def getHandle():
    """
    Find the Minecraft process handle and return the handle.
     - Return ``Win32Window`` class that includes the handle information.
     - Return ``False`` if the Minecraft process currently does not exist. 
    """

    # Grab all windows titles that currently open.
    titles = gw.getAllTitles()

    # Find the Minecraft process and obtain the handle.
    for t in titles:
        if 'Minecraft' in t and 'Launcher' not in t:
            handle = gw.getWindowsWithTitle(t)
            print(f'{langData["Text2"]} ({t}, Handle: {handle[0]._hWnd})') # [Info] Minecraft handle captured!
            return handle[0]
    return False

def detectImage(handle):
    """
    Matching the Minecraft subtitles with pre-captured images by using the OpenCV.
     - Return ``True`` if the subtitle matches with a pre-captured subtitle image.
     - Return ``False`` if the subtitle did not match with a pre-captured subtitle image.
     - Return ``None`` if an error occurred.
    """

    # Find Minecraft's window information.
    try:
        x1, y1, x2, y2 = handle._getWindowRect()
    except:
        print(langData['Text3']) # [Exit] Game is not running.
        return None

    # Calculate the optimized capturing area for better performance.
    w = handle.width
    h = handle.height
    p1 = (x1 + int(w/2), y1 + int(h/3))
    p2 = (int(w/2), int(h/3*2))

    try:
        # Capture the Game window.
        imageOriginal = np.array(pyautogui.screenshot(region=p1+p2))
        if preview == 0:
            cv2.imshow('Preview', imageOriginal)
            cv2.waitKey(1)
        else:
            cv2.destroyAllWindows()

        image = cv2.cvtColor(imageOriginal, cv2.COLOR_BGR2GRAY)
        
        # Do image matching by using multi-scale target sample image and actual captured game image.
        loc = False
        w, h = target.shape[::-1]
        for scale in np.linspace(0.8, 2.0, 30)[::-1]:
            # Resizing
            resized = imutils.resize(target, width = int(target.shape[1] * scale))
            w, h = resized.shape[::-1]
            try:
                res = cv2.matchTemplate(image, resized, cv2.TM_CCOEFF_NORMED)
            except Exception as e:
                if '_img.size().height' in str(e):
                    print(langData['Text4']) # [Error] Game window is too small. Resize the window a little bit bigger.
                    time.sleep(1)
                    return False
                else:
                    # Unknown error handling.
                    print(langData['Text5']) # [Error] Template matching failed.
                    print(e)
                    return None
            loc = np.where(res >= accuracy)
            if len(list(zip(*loc[::-1]))) > 0:
                break # Image detected.

        if loc and len(list(zip(*loc[::-1]))) > 0:
            for pt in zip(*loc[::-1]):
                # Draw a rectangle on the detected area.
                if preview != 2:
                    cv2.rectangle(imageOriginal, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
                    cv2.imshow('Preview', imageOriginal)
                    cv2.waitKey(1)
                else:
                    cv2.destroyAllWindows()
                return True

    except Exception as e:
        # Unknown error handling.
        print(langData['Text6']) # [Error] An unexpected error occurred.
        print(e)
        return None
    return False

# Main Run
total = 1
handle = getHandle()
if handle is False:
    print(langData['Text7']) # [Info] Cannot find the Minecraft process. Continue to search the game processor...

while vaild:
    if handle is not False:
        capture = detectImage(handle)
        if capture is None:
            break

        if capture:
            print(f'{langData["Text8"]}{total}') # [Info] Detected! - Total: 
            total += 1
            pyautogui.click(button='right')
            time.sleep(0.5)
            pyautogui.click(button='right')
            time.sleep(4)
        time.sleep(delay)
    else:
        time.sleep(2)
        handle = getHandle()

cv2.destroyAllWindows()
input(langData['Text9']) # Press enter to exit...