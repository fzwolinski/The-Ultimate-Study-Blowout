import sys
import json
import pygetwindow
import win32gui
import win32ui
from ctypes import windll
from PIL import Image
import pathlib
import time
import numpy as np
import cv2

class SmartStudent:
  def __init__(self, flags=[]):
    if len(flags) > 0:
      self.handle_flags(flags)
    self.load_config()
    # Window handle is necessary
    self.check_window_attribute()
    self.main_loop()

  def load_config(self):
    try:
      with open('config.json') as f:
        self.config = json.load(f)
    except:
      print("Error opening config file. File may be missing or may be empty.")
      print("Loading default config. You must specify SCREENSHOT WINDOW by running\n"
            "python main.py -w")
      self.config = self.default_config()
      self.write_config_to_file()
      # We exit, because program can't run without specified window name
      sys.exit()

  def write_config_to_file(self):
    with open('config.json', 'w') as f:
      json.dump(self.config, f)

  def default_config(self):
    return  {
      "window": "",
      "step": 15,     # Take screenshot every 15s
      "ss_path": "",
      "diff_percentage": 5
    }

  def check_window_attribute(self):
    if "window" not in self.config.keys():
      sys.exit("Wrong window attribute.\n"
        "Either check config file or run python main.py -w")
    elif not self.config["window"] or not isinstance(self.config["window"], str):
      sys.exit("Wrong window attribute.\n"
        "Either check config file or [run python main.py -w]")

  def print_available_windows(self):
    print("\nThese are the names of the windows that are currently active. \n"
      "Copy name of window whose screenshots you will be saving and paste it to Your config file.\n"
      "Example (in config file):\n\"window\": \"Microsoft Teams\",")
    print("----------------------------------")
    for title in pygetwindow.getAllTitles():
      if title:
        print(title)
    print("----------------------------------")

  def flags_description(self):
    return """Available flags
  -w\tdisplay active windows
  -t\ttest screenshot
\nexample: python main.py -w
    """

  def handle_flags(self, f):
    # If none of the flags provided is valid,
    # we want to inform user about it
    flags_message = self.flags_description()
    
    if "-w" in f:
      self.print_available_windows()
      flags_message = ""
    if "-t" in f:
      # TODO
      flags_message = ""
      
    # Flags are only for displaying information
    # We don't want to run screenshot program
    sys.exit(flags_message)

  def main_loop(self):
    # TODO: Max images [ITERATIONS]
    ITERATIONS = 5
    i = 0
    while True:
      self.take_screenshot(self.config["window"], self.config["ss_path"], str(i))
      if i > 0:
        img1 = self.config["ss_path"] + "/" + str(i-1) + ".jpg"
        img2 = self.config["ss_path"] + "/" + str(i) + ".jpg"
        print("Diff between {} and {} = {}%".format(img1, img2, self.percentage_diff_between_two_imgs(img1, img2)))
        
        # If difference between two images is too small, it means slide wasnt changed
        # We want to delete this image in order not to have img duplicates
        if self.percentage_diff_between_two_imgs(img1, img2) < int(self.config["diff_percentage"]):
          try:
            pathlib.Path(img2).unlink()
          except:
            pass
          i -= 1

      time.sleep(self.config["step"])
      i += 1

      ITERATIONS -= 1
      if ITERATIONS == 0:
        sys.exit()


  def take_screenshot(self, window, path, img_name):
    # https://stackoverflow.com/a/24352388

    hwnd = win32gui.FindWindow(None, window)
    if hwnd == 0:
      sys.exit("Wrong window name.\n"
        "Check window names running [python main.py -w]")

    left, top, right, bot = win32gui.GetClientRect(hwnd)
    #left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    saveDC.SelectObject(saveBitMap)

    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
    
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    ss_img = path + "/" + (img_name + ".jpg")
    
    if result == 1:
      im.save(ss_img)

  def percentage_diff_between_two_imgs(self, img1, img2):
    img1, img2 = cv2.imread(img1, 0), cv2.imread(img2, 0)
    diff = cv2.absdiff(img1, img2)
    diff = diff.astype(np.uint8)
    percentage_diff = (np.count_nonzero(diff) * 100) / diff.size
    return percentage_diff