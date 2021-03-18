import sys
import json
import pygetwindow
import win32gui
import win32ui
from ctypes import windll
from PIL import Image
import pathlib
import time
import imgcompare
import os
import threading
from pynput import keyboard
import pyautogui as pg

class SmartStudent:
  def __init__(self):
    self.output = ""
    self.load_config()
    # Window handle is necessary
    self.check_window_attribute()
    #self.main_loop()
    self.stop = False

  def load_config(self):
    try:
      with open('config.json') as f:
        self.config = json.load(f)
    except:
      print("Error opening config file. File may be missing or may be empty.")
      print("Loading default config. You must specify SCREENSHOT WINDOW in Config Tab\n")
      self.config = self.default_config()
      self.write_config_to_file(self.config)

  def write_config_to_file(self, c):
    try: 
      with open('config.json', 'w') as f:
        self.config.update(c)
        json.dump(self.config, f)
      return 1
    except:
      return 0

  def default_config(self):
    return  {
      "window_id": 0,
      "step": 10,     # Take screenshot every 15s
      "ss_path": "imgs",
      "diff_percentage": 0.9,
      "window_pos": {"x": 0, "y": 0},
      "top_left_coords": {},
      "bottom_right_coords": {}
    }

  def check_window_attribute(self):
    if "window_id" not in self.config.keys():
      print("Wrong window attribute. Check Config Tab")
    elif not self.config["window_id"] or not isinstance(self.config["window_id"], int):
      print("Wrong window attribute. Check Config Tab")

    # If window_id is incorrect, get first correct one and save it
    available_windows = self.available_windows()
    window_names = [x for x in available_windows.values()]

    if not str(self.config["window_id"]) in available_windows.keys():
      self.config["window_id"] = int(list(available_windows.keys())[0])
      self.write_config_to_file(self.config)

  def available_windows(self):
    #print("These are the ID's and names of the windows that are currently active. \n"
    #  "Copy ID of window whose screenshots you will be saving and paste it to Your config file.\n"
    #  "Example (in config file):\n\"window_id\": 328696,")
    #print("----------------------------------")
    windows = {}
    for title in pygetwindow.getAllTitles():
      if title:
        windows[str(pygetwindow.getWindowsWithTitle(title)[0]._hWnd)] = title 
    return windows
    #print("----------------------------------")

  def take_test_screenshot(self):
    self.load_config()
    self.check_window_attribute()
    if self.take_screenshot(self.config["window_id"], self.config["ss_path"], "test") != -1:
      print("Test screenshot:\n"
            "IMG Name: test.jpg\n"
            "Path: {}\n"
            "Window ID: {}\n"
            .format(self.config["ss_path"], self.config["window_id"])
      )

  def run(self):
    self.stop = False
    run_thread = threading.Thread(target=self.main_loop)
    run_thread.start()

  def stop_program(self):
    self.stop = True

  def main_loop(self):
    # TODO: Max images [ITERATIONS]
    i = self.start_img_number(self.config["ss_path"])
    print("Starting with {}.jpg\n".format(i))
    while True:
      if self.take_screenshot(self.config["window_id"], self.config["ss_path"], str(i)) == -1:
        self.stop_program()
        return
      if i > 0:
        if self.config["ss_path"]:
          img1 = pathlib.Path(self.config["ss_path"]) / (str(i-1) + ".jpg")
          img2 = pathlib.Path(self.config["ss_path"]) / (str(i) + ".jpg")
        else:
          img1 = str(i-1) + ".jpg"
          img2 = str(i) + ".jpg"

        print("Diff between {} and {} = {:.5f}%"
              .format(str(i-1) + ".jpg", str(i) + ".jpg", self.percentage_diff_between_two_imgs(img1, img2)))
        
        # If difference between two images is too small, it means slide wasnt changed
        # We want to delete this image in order not to have img duplicates
        if self.percentage_diff_between_two_imgs(img1, img2) < float(self.config["diff_percentage"]):
          try:
            pathlib.Path(img2).unlink()
          except:
            pass
          i -= 1

      time.sleep(self.config["step"])
      i += 1

      if self.stop:
        return


  def take_screenshot(self, window, path, img_name):
    # https://stackoverflow.com/a/24352388

    #hwnd = win32gui.FindWindow(None, "window")
    hwnd = window
    if hwnd == 0:
      print("Wrong window ID.\n")
      return -1
    
    try:
      left, top, right, bot = win32gui.GetClientRect(hwnd)
    except:
      print("Wrong window ID.\n")
      return -1
  
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

    # Crop image
    if self.config.get("top_left_coords") and self.config.get("bottom_right_coords"):
      top_left_x, top_left_y, _, _ = win32gui.GetWindowRect(hwnd)
      x1, y1, x2, y2 = self.get_rel_crop_coords(top_left_x, top_left_y)
      im = im.crop((x1, y1, x2, y2))
    
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    if path:
      #ss_img = path + "/" + (img_name + ".jpg")
      ss_img = pathlib.Path(path) / (img_name + ".jpg")
    else:
      ss_img = img_name + ".jpg"

    if result == 1:
      im.save(ss_img)

  def percentage_diff_between_two_imgs(self, img1, img2):
    # Check if resolution of both images are the same
    # If not, we can not compare them
    i1, i2 = Image.open(img1), Image.open(img2)
    if not (i1.size == i2.size):
      return 100

    return imgcompare.image_diff_percent(i1, i2)

  def start_img_number(self, path):
    """
    As we start program, we don't want to just start
    saving screenshots from like 0.jpg, 1.jpg...
    because they will overwrite any screenshots previously taken.
    start_img_number returns the number of the photo 
    from which we start taking screenshots

    0 <- start with 0.jpg
    """

    img_names = []

    try:
      for file in os.listdir(path):
          if file.endswith(".jpg"):
            img_names.append(int(file.replace(".jpg", "")))
      if img_names:
        img_names.sort()
        return img_names[-1] + 1
      else:
        return 0

    except:
      return 0

  def set_ss_coords(self, curr_win_id):
    self.top_left_coords = {}
    self.bottom_right_coords = {}

    def on_press(key):
      if key == keyboard.Key.f1:
        top_left = {
          "x": pg.position()[0],
          "y": pg.position()[1]
        }
        self.top_left_coords = top_left
      elif key == keyboard.Key.f2:
        bottom_right = {
          "x": pg.position()[0],
          "y": pg.position()[1]
        }
        self.bottom_right_coords = bottom_right
      if (self.top_left_coords and self.bottom_right_coords) or key == keyboard.Key.esc:
        return False # Stop listener

    l1 = keyboard.Listener(on_press=on_press)
    l1.start()
    l1.join()

    x1, y1, x2, y2 = win32gui.GetWindowRect(curr_win_id)
    
    if self.top_left_coords and self.bottom_right_coords:
      # Check if TOP_LEFT corner is above BOTTOM_RIGHT corner of rectangle
      if not ((self.top_left_coords["x"] < self.bottom_right_coords["x"]) and 
              (self.top_left_coords["y"] < self.bottom_right_coords["y"])):
        return -1

      # Check if selected coords fit the window area
      if (self.top_left_coords["x"] < x1 or self.bottom_right_coords["x"] > x2 or
          self.top_left_coords["y"] < y1 or self.bottom_right_coords["y"] > y2):
        return -1

      # If coords are correct, we want to store window position
      # in order to shift ss area while moving window
      self.config["window_pos"]["x"] = x1
      self.config["window_pos"]["y"] = y1

      return self.top_left_coords, self.bottom_right_coords

    return -1

  def get_rel_crop_coords(self, tl_x, tl_y):
    tl_mouse_x = self.config.get("top_left_coords").get("x")
    tl_mouse_y = self.config.get("top_left_coords").get("y")
    br_mouse_x = self.config.get("bottom_right_coords").get("x")
    br_mouse_y = self.config.get("bottom_right_coords").get("y")

    # Calculate window movement
    x_shift = tl_x - self.config["window_pos"]["x"]
    y_shitf = tl_y - self.config["window_pos"]["y"]

    # x1, y2 - top left
    x1 = tl_mouse_x - tl_x + x_shift
    y1 = tl_mouse_y - tl_y + y_shitf

    # x2, y2 - bottom right
    x2 = br_mouse_x - tl_x + x_shift
    y2 = br_mouse_y - tl_y + y_shitf

    return x1, y1, x2, y2