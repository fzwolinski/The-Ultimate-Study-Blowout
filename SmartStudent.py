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
    self.output = []
    self.load_config()
    self.load_translation()
    self.set_available_themes()
    # Window handle is necessary
    self.check_window_attribute()
    self.stop = True

  def load_translation(self):
    try:
      with open(f"langs/{self.config['lang']}.json") as f:
        self.outputs = json.load(f)['outputs']
    except:
      pass

    self.set_available_translations_config()
  
  def set_available_translations_config(self):
    available_langs = []
    try:
      for lang in os.listdir("langs"):
          if lang.endswith(".json"):
            available_langs.append(lang.replace(".json", ""))
    except:
      pass
  
    self.config["available_langs"] = available_langs
    self.write_config_to_file(self.config)
  
  def set_language(self, lang):
    if (lang in self.get_available_translations() and 
        lang != self.config["lang"]):
      self.config["lang"] = lang
      self.write_config_to_file(self.config)
      return True
    return False

  def get_available_translations(self):
    return self.config["available_langs"]

  def set_available_themes(self):
    available_themes = []
    try:
      for theme in os.listdir("themes"):
        if theme.endswith(".json"):
          available_themes.append(theme.replace(".json", ""))
    except:
      pass
  
    self.config["available_themes"] = available_themes
    self.write_config_to_file(self.config)

  def set_theme(self, theme):
    if (theme in self.get_available_themes() and 
        theme != self.config["theme"]):
      self.config["theme"] = theme
      self.write_config_to_file(self.config)
      return True
    return False

  def get_available_themes(self):
    return self.config["available_themes"]

  def load_config(self):
    try:
      with open('config.json') as f:
        config_file = json.load(f)
        self.config = config_file
        if self.config['current_profile'] in self.get_profiles():
          self.config_profile = self.config['profile'][self.config['current_profile']]
        else:
          self.set_active_profile("default")
    except:
      self.output.append(self.outputs['file_open_err'])
      self.config = self.get_default_config()
      self.config_profile = self.config['profile']['default']      
      self.write_config_to_file(self.config)

  def write_config_to_file(self, c):
    try:
      with open('config.json', 'w') as f:
        json.dump(self.config, f)
      return 1
    except:
      return 0

  def update_config_profile(self, p, c):
    try:
      with open('config.json', 'w') as f:
        self.config['profile'][p].update(c)
        json.dump(self.config, f)
      return 1
    except:
      return 0

  def get_default_config(self):
    return  {
      "lang": "en",
      "available_langs": [],
      "theme": "light",
      "available_themes": [],
      "current_profile": "default",
      "profile": {
        "default": {
          "window_id": 0,
          "step": 5,
          "ss_path": "imgs",
          "diff_percentage": 2,
          "window_pos": {},
          "top_left_coords": {},
          "bottom_right_coords": {},
          "crop_img": False
        }
      }
    }

  def set_active_profile(self, p):
    if p in self.get_profiles():
      self.config['current_profile'] = p
      self.config_profile = self.config['profile'][p]
      self.write_config_to_file(self.config['profile'])
      return True
    return False

  def create_new_profile(self, name, body):
    if name not in self.get_profiles():
      blank_body = self.get_default_config()['profile']['default']
      blank_body.update(body)
      self.config['profile'][name] = blank_body
      self.config['current_profile'] = name
      self.write_config_to_file(self.config)
      return True
    return False

  def get_profiles(self):
    return list(self.config['profile'].keys())

  def rename_profile(self, old, new):
    if (old in self.get_profiles() and 
        new not in self.get_profiles() and 
        old != "default"):
      # Both rename profile and change current_profile if old one was active
      if self.config['current_profile'] == old:
        self.config['current_profile'] = new
      self.config['profile'][new] = self.config['profile'].pop(old)
      self.write_config_to_file(self.config)
      return True
    return False

  def delete_profile(self, name):
    if name not in self.get_profiles() or name == "default":
      return False
    self.config['profile'].pop(name)
    self.write_config_to_file(self.config)
    return True

  def get_output(self):
    return self.output, len(self.output)

  def check_window_attribute(self):
    if "window_id" not in self.config_profile.keys():
      self.output.append(self.outputs['window_id_err'])
    elif (not self.config_profile['window_id'] or 
          not isinstance(self.config_profile['window_id'], int)):
      self.output.append(self.outputs['window_id_err'])

    # If window_id is incorrect, get first correct one and save it
    available_windows = self.get_available_windows()
    window_names = [x for x in available_windows.values()]

    if not str(self.config_profile['window_id']) in available_windows.keys():
      self.config_profile['window_id'] = int(list(available_windows.keys())[0])
      self.update_config_profile(self.config['current_profile'], self.config_profile)

  def get_available_windows(self):
    windows = {}
    for title in pygetwindow.getAllTitles():
      if title:
        windows[str(pygetwindow.getWindowsWithTitle(title)[0]._hWnd)] = title
    return windows

  def take_test_screenshot(self):
    self.load_config()
    self.check_window_attribute()
    if (self.take_screenshot(
          self.config_profile['window_id'], 
          self.config_profile['ss_path'], "test") != -1):
      self.output.append(
            "{}:\n"
            "{}: test.jpg\n"
            "{}: {}\n"
            "{}: {}"
            .format(
              self.outputs['test_screenshot'],
              self.outputs['img_name'],
              self.outputs['path'],
              self.config_profile['ss_path'],
              self.outputs['window_id'],
              self.config_profile['window_id'])
      )

  def run(self):
    self.stop = False
    run_thread = threading.Thread(target=self.main_loop)
    run_thread.start()
    
  def stop_program(self):
    self.stop = True

  def main_loop(self):
    i = self.start_img_number(self.config_profile['ss_path'])
    self.output.append(f"{self.outputs['starting_with']} {i}.jpg")

    while not self.stop:
      if (self.take_screenshot(
            self.config_profile['window_id'], 
            self.config_profile['ss_path'], str(i)) == -1):
        self.stop_program()
        return
      if i > 0:
        if self.config_profile['ss_path']:
          img1 = pathlib.Path(self.config_profile['ss_path']) / (str(i-1) + ".jpg")
          img2 = pathlib.Path(self.config_profile['ss_path']) / (str(i) + ".jpg")
        else:
          img1 = str(i-1) + ".jpg"
          img2 = str(i) + ".jpg"

        self.output.append("{} {} {} {} = {:.5f}%"
              .format(self.outputs['diff_between'], 
                      str(i-1) + ".jpg", 
                      self.outputs['and'], 
                      str(i) + ".jpg", 
                      self.percentage_diff_between_two_imgs(img1, img2)
                      ))
        
        # If difference between two images is too small, it means slide wasnt changed
        # We want to delete this image in order not to have img duplicates
        if (self.percentage_diff_between_two_imgs(img1, img2) <
            float(self.config_profile['diff_percentage'])):
          try:
            pathlib.Path(img2).unlink()
          except:
            pass
          i -= 1

      time.sleep(self.config_profile['step'])
      i += 1

  def take_screenshot(self, window, path, img_name):
    # https://stackoverflow.com/a/24352388

    hwnd = window
    if hwnd == 0:
      self.output.append(self.outputs['wrong_window_id'])
      return -1
    
    try:
      left, top, right, bot = win32gui.GetClientRect(hwnd)
    except:
      self.output.append(self.outputs['wrong_window_id'])
      return -1
  
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
    if (self.config_profile['crop_img'] and 
        self.config_profile.get("top_left_coords") and 
        self.config_profile.get("bottom_right_coords")):
      top_left_x, top_left_y, _, _ = win32gui.GetWindowRect(hwnd)
      x1, y1, x2, y2 = self.get_rel_crop_coords(top_left_x, top_left_y)
      im = im.crop((x1, y1, x2, y2))
    
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    if path:
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
          if (file.replace(".jpg", "")).isnumeric():
            img_names.append(int(file.replace(".jpg", "")))
    except:
      return 0
    
    if img_names:
      img_names.sort()
      return img_names[-1] + 1
    else:
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
      if ((self.top_left_coords and self.bottom_right_coords) or 
           key == keyboard.Key.esc):
        return False # Stop listener

    l1 = keyboard.Listener(on_press=on_press)
    l1.start()
    l1.join()

    x1, y1, x2, y2 = win32gui.GetWindowRect(curr_win_id)
    
    if self.top_left_coords and self.bottom_right_coords:
      # Check if TOP_LEFT corner is above BOTTOM_RIGHT corner of rectangle
      if not ((self.top_left_coords['x'] < self.bottom_right_coords['x']) and 
              (self.top_left_coords['y'] < self.bottom_right_coords['y'])):
        return -1

      # Check if selected coords fit the window area
      if (self.top_left_coords['x'] < x1 or self.bottom_right_coords['x'] > x2 or
          self.top_left_coords['y'] < y1 or self.bottom_right_coords['y'] > y2):
        return -1

      # If coords are correct, we want to store window position
      # in order to shift ss area while moving window
      self.config_profile['window_pos']['x'] = x1
      self.config_profile['window_pos']['y'] = y1

      return self.top_left_coords, self.bottom_right_coords
    return -1

  def get_rel_crop_coords(self, tl_x, tl_y):
    tl_mouse_x = self.config_profile.get("top_left_coords").get("x")
    tl_mouse_y = self.config_profile.get("top_left_coords").get("y")
    br_mouse_x = self.config_profile.get("bottom_right_coords").get("x")
    br_mouse_y = self.config_profile.get("bottom_right_coords").get("y")

    # Calculate window movement
    x_shift = tl_x - self.config_profile['window_pos']['x']
    y_shitf = tl_y - self.config_profile['window_pos']['y']

    # x1, y2 - top left
    x1 = tl_mouse_x - tl_x + x_shift
    y1 = tl_mouse_y - tl_y + y_shitf

    # x2, y2 - bottom right
    x2 = br_mouse_x - tl_x + x_shift
    y2 = br_mouse_y - tl_y + y_shitf

    return x1, y1, x2, y2