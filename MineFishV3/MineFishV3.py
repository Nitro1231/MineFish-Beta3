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
# ✔ Validate the config file.
# Add update check method.
# Add easy setting setup or auto setting detection function.
# Reorganize and optimize the code.

import os
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
if (os.path.exists('./config.ini')):
    config = configparser.ConfigParser()
    config.read('./config.ini', encoding='utf-8')
    textImage = f'./Core/img/{config.get("MineFishV3 Setting", "image").strip()}'
    langType = config.get('MineFishV3 Setting', 'language')

    # Read language file.
    if (os.path.exists('./Core/Language.json')):
        with open('./Core/Language.json', encoding='utf-8') as f:
            lang = json.load(f)
        try:
            langData = lang[langType]
        except:
            print(f'[Error] Language "{langType}" is currently not available.')
            print('Supportive languages are listed below:')
            for key in lang.keys():
                print(key)
            exit()
    else:
        print('[Error] The language file is missing, please re-download the software here: https://github.com/Nitro1231/MineFish-V3/releases')
        exit()

    if (not os.path.exists(textImage)):
        print(langData['Text19']) # [Error] The image file does not exist. Please check if the image file exists in the "./Core/img" folder.
        quit()

    try:
        delay = float(config.get('MineFishV3 Setting', 'delay'))
        accuracy = float(config.get('MineFishV3 Setting', 'accuracy')) # 0.5 < accuracy < 1
        preview = int(config.get('MineFishV3 Setting', 'preview')) # 0 <= preview <= 2
    except Exception as e:
        print(f'{langData["Text20"]}\n') # [Error] One of the config file variables is not correct. Please check if the delay and accuracy variable is in form of float, and check if the preview variable is in form of an integer.
        print(e)
        quit()

    if (not(accuracy < 1 and accuracy > 0.5)):
        print(langData['Text21']) # [Error] The accuracy variable must be in the range between 0.5 and 1.0.
        quit()

    if (not(preview >= 0 and preview <= 2)):
        print(langData['Text22']) # [Error] The preview variable must be 0, 1, or 2. The meaning of each number is as below:
        print(f'0. {langData["Text16"]}')
        print(f'1. {langData["Text17"]}')
        print(f'2. {langData["Text18"]}')
        quit()

    if delay <= 0:
        print(langData['Text23']) # [Error] The delay variable must be a positive number.
        quit()
    elif delay >= 1:
        print(langData['Text24']) # [Warning] Delay is too long. This might make this program hard to detect fishing status. Please keep the delay under 1 second.
else:
    print('[Error] The config file is missing, please re-download the software here: https://github.com/Nitro1231/MineFish-V3/releases')
    quit()

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

while True:
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