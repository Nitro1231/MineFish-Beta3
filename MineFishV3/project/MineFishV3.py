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

# TODO for V 3.0.1:
# ✔ Add Preview Mode Method.
# ✔ Add a config helper methood.
# ✔ Add update check method.
# ✔ Add easy setting setup or auto setting detection function.
# Add the method that tracks and writes the terminal outputs for future feedback and error tracing.
# Reorganize and optimize the code.

# TODO for Next:


import os
import cv2
import time
import json
import imutils
import requests
import pyautogui
import configparser
import numpy as np
import pygetwindow as gw

ver = '3.0.1'
# sys.stdout = open('./Debug Log.txt', 'w')

# region Basic Info
# Print basic information.
print(",--.   ,--.,--.               ,------.,--.       ,--.         ,--.   ,--.,----.  \n|   `.'   |`--',--,--,  ,---. |  .---'`--' ,---. |  ,---.      \  `.'  / '.-.  | \n|  |'.'|  |,--.|      \| .-. :|  `--, ,--.(  .-' |  .-.  |      \     /    .' <  \n|  |   |  ||  ||  ||  |\   --.|  |`   |  |.-'  `)|  | |  |       \   /   /'-'  | \n`--'   `--'`--'`--''--' `----'`--'    `--'`----' `--' `--'        `-'    `----'  ")
print(f'{"=" * 10}Info{"=" * 10}')
print('Developer: Nitro')
print('Email: admin@nitrostudio.dev')
print('Blog: http://blog.nitrostudio.dev/')
print('Discord: Nitro#1781\n')
print(f'Build: {ver}\n')
# endregion


def ex():
    input('Press enter to exit...')
    # sys.stdout.close()
    quit()


# region Config and Initialization
# Read config file.
config_file = './config.ini'
if (os.path.exists(config_file)):
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')

    # region User config setup
    # Read language file.
    if (os.path.exists('./Core/Language.json')):
        with open('./Core/Language.json', encoding='utf-8') as f:
            lang = json.load(f)

        is_vaild_lang = False
        lang_type = config.get('MineFishV3 Setting', 'language')
        while(is_vaild_lang == False):
            try:
                lang_data = lang[lang_type]
                config.set('MineFishV3 Setting', 'language', lang_type)
                is_vaild_lang = True
            except:
                # Invalid config value. Give users the possible options and ask them to manually set the value.
                print(f'[Error] Language "{lang_type}" is currently not available.')
                print('Supportive languages are listed below:')
                for key in lang.keys():
                    print(key)

                print()
                lang_type = input('Type one of the language that listed above: ')
                print()
    else:
        print('[Error] The language file is missing, please re-download the software here: https://github.com/Nitro1231/MineFish-V3/releases')
        ex()

    # Text Image
    is_vaild_image = False
    text_image = config.get('MineFishV3 Setting', 'image').strip()
    while(is_vaild_image == False):
        img_list = []
        for image in os.listdir('./Core/img'):
            img_list.append(image)
            if text_image.strip() == image:
                config.set('MineFishV3 Setting', 'image', image)
                is_vaild_image = True

        # No files in the image folder. Pretend that there is a file and throw an error after escaping the loop.
        if len(img_list) <= 0:
            is_vaild_image = True

        if is_vaild_image == False:
            # Invalid config value. Give users the possible options and ask them to manually set the value.
            # "[Error] Invalid image file name detected. Please choose one from the list:"
            print(lang_data['Text26'])
            for image in img_list:
                print(image)
            print()
            # "Type one of the file name that listed above: "
            text_image = input(lang_data['Text27']).strip()
            print()
    text_image = f'./Core/img/{text_image}'

    if (not os.path.exists(text_image)):
        # "[Error] The image file does not exist. Please check if the image file exists in the "./Core/img" folder."
        print(lang_data['Text19'])
        ex()

    # Save changes
    config.write(open(config_file, 'w'))
    # endregion

    try:
        delay = float(config.get('MineFishV3 Setting', 'delay'))
        # 0.5 < accuracy < 1
        accuracy = float(config.get('MineFishV3 Setting', 'accuracy'))
        # 0 <= preview <= 2
        preview = int(config.get('MineFishV3 Setting', 'preview'))
    except Exception as e:
        # [Error] One of the config file variables is not correct. Please check if the delay and accuracy variable is in form of float, and check if the preview variable is in form of an integer.
        print(f'{lang_data["Text20"]}\n')
        print(e)
        ex()

    if (not(accuracy < 1 and accuracy > 0.5)):
        # [Error] The accuracy variable must be in the range between 0.5 and 1.0.
        print(lang_data['Text21'])
        ex()

    if (not(preview >= 0 and preview <= 2)):
        # [Error] The preview variable must be 0, 1, or 2. The meaning of each number is as below:
        print(lang_data['Text22'])
        print(f'0. {lang_data["Text16"]}')
        print(f'1. {lang_data["Text17"]}')
        print(f'2. {lang_data["Text18"]}')
        ex()

    if delay <= 0:
        # [Error] The delay variable must be a positive number.
        print(lang_data['Text23'])
        ex()
    elif delay >= 1:
        # [Warning] Delay is too long. This might make this program hard to detect fishing status. Please keep the delay under 1 second.
        print(lang_data['Text24'])
else:
    print('[Error] The config file is missing, please re-download the software here: https://github.com/Nitro1231/MineFish-V3/releases')
    ex()

# Load a description for preview mode.
if preview == 1:
    preview_mode = lang_data['Text17']
elif preview == 2:
    preview_mode = lang_data['Text18']
else:
    preview_mode = lang_data['Text16']

# Print the current setting.
print(f'{"=" * 10}{lang_data["Text10"]}{"=" * 10}')  # Setting
print(f'{lang_data["Text11"]}"{text_image}"')  # Image File:
print(f'{lang_data["Text12"]}{lang_type}')  # Language:
print(f'{lang_data["Text13"]}{delay}')  # Delay:
print(f'{lang_data["Text14"]}{accuracy}')  # Threshold:
print(f'{lang_data["Text15"]}{preview} ({preview_mode})')  # Preview Mode:

# Check if there is any other version available
req = requests.get('https://raw.githubusercontent.com/Nitro1231/MineFish-V3/main/ver.txt')
latest_version = req.text.strip()
if (not (req.status_code == 200 and ver == latest_version)):
    print()
    print(lang_data['Text25'])

# Load the target image and convert it into grayscale.
target = cv2.imread(text_image)
target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

print()
print(lang_data['Text1'])  # [Info] Initialized completed.
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
            # "[Info] Minecraft handle captured!""
            print(f'{lang_data["Text2"]} ({t}, Handle: {handle[0]._hWnd})')
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
        print(lang_data['Text3'])  # "[Exit] Game is not running."
        return None

    # Calculate the optimized capturing area for better performance.
    w = handle.width
    h = handle.height
    p1 = (x1 + int(w/2), y1 + int(h/3))
    p2 = (int(w/2), int(h/3*2))

    try:
        # Capture the Game window.
        image_original = np.array(pyautogui.screenshot(region=p1+p2))
        if preview == 0:
            cv2.imshow('Preview', image_original)
            cv2.waitKey(1)
        else:
            cv2.destroyAllWindows()

        image = cv2.cvtColor(image_original, cv2.COLOR_BGR2GRAY)

        # Do image matching by using multi-scale target sample image and actual captured game image.
        loc = False
        w, h = target.shape[::-1]

        suitable_size = False
        for scale in np.linspace(0.8, 2.0, 30)[::-1]:
            # Resizing
            resized = imutils.resize(
                target, width=int(target.shape[1] * scale))
            w, h = resized.shape[::-1]
            try:
                res = cv2.matchTemplate(image, resized, cv2.TM_CCOEFF_NORMED)
                suitable_size = True
            except Exception as e:
                if '_img.size().height' not in str(e):
                    # Unknown error handling.
                    # "[Error] Template matching failed."
                    print(lang_data['Text5'])
                    print(e)
                    return None

            loc = np.where(res >= accuracy)
            if len(list(zip(*loc[::-1]))) > 0:
                break  # Image detected.
        
        if suitable_size == False:
            # "[Error] Game window is too small. Resize the window a little bit bigger."
            print(lang_data['Text4'])
            time.sleep(1)
            return False

        if loc and len(list(zip(*loc[::-1]))) > 0:
            for pt in zip(*loc[::-1]):
                # Draw a rectangle on the detected area.
                if preview != 2:
                    cv2.rectangle(image_original, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
                    cv2.imshow('Preview', image_original)
                    cv2.waitKey(1)
                else:
                    cv2.destroyAllWindows()
                return True

    except Exception as e:
        # Unknown error handling.
        print(lang_data['Text6'])  # "[Error] An unexpected error occurred."
        print(e)
        return None
    return False


# Main Run
total = 1
handle = getHandle()
if handle is False:
    # "[Info] Cannot find the Minecraft process. Continue to search the game processor..."
    print(lang_data['Text7'])

while True:
    if handle is not False:
        capture = detectImage(handle)
        if capture is None:
            break

        if capture:
            print(f'{lang_data["Text8"]}{total}')  # "[Info] Detected! - Total: "
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
ex()
