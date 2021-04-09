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

# TUSB - The Ultimate Study Blowout
class TUSB:
  def __init__(self):
    # Gui output messages
    self.output = []
    
    #Load essentials
    self.load_config()
    self.load_translation()
    self.set_available_themes()
    
    # Window handle is necessary
    self.check_window_attribute()
    
    # Main loop stopper
    self.stop = True

  def load_translation(self):
    """
    Load messages, outputs in currently set language
    """
    try:
      with open(f"langs/{self.config['lang']}.json") as f:
        self.outputs = json.load(f)['outputs']
    except:
      pass

    # Every time opening program, 
    # check available translations
    self.set_available_translations_config()
  
  def set_available_translations_config(self):
    """
    Scan /langs folder for available translations
    Next add them to config file
    """
    available_langs = []
    try:
      for lang in os.listdir("langs"):
          if lang.endswith(".json"):
            available_langs.append(lang.replace(".json", ""))
    except:
      pass
  
    self.config["available_langs"] = available_langs
    # Save config with translations to file
    self.write_config_to_file(self.config)
  
  def set_language(self, lang):
    """
    Allows to change current language of application (from GUI)

    :param lang: language abbreviation e.g. "en", "pl"
    :return:
        True if succeeded
        False if failed
    """

    # Check if language from parameter is correct (available)
    # and if its different from the one currently set
    if (lang in self.get_available_translations() and 
        lang != self.config["lang"]):
      self.config["lang"] = lang
      self.write_config_to_file(self.config)
      return True
    return False

  def get_available_translations(self):
    """
    :return: list of available languages
    """
    return self.config["available_langs"]

  def set_available_themes(self):
    """
    Scan /themes folder for available themes
    Next add them to config file    
    """
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
    """
    Allows to change theme of application (from GUI)

    :param theme: theme name e.g. "dark", "light"
    :return:
      True if succeeded
      False if failed
    """

    # Check if theme from parameter is correct (available)
    # and if its different from the one currently set
    if (theme in self.get_available_themes() and 
        theme != self.config["theme"]):
      self.config["theme"] = theme
      self.write_config_to_file(self.config)
      return True
    return False

  def get_available_themes(self):
    """
    :return: list of available themes
    """
    return self.config["available_themes"]

  def load_config(self):
    """
    Opens config file. If it exists loads its content.
    If it doesn't exist gets default config scheme from 
    self.get_default_config() function and saves it to config.json file
    Also loads current config profile
    """
    try:
      with open('config.json') as f:
        config_file = json.load(f)
        self.config = config_file
        # Check if currently set profile even exists
        if self.config['current_profile'] in self.get_profiles():
          # Profile exists. Load its attributes
          self.config_profile = self.config['profile'][self.config['current_profile']]
        else:
          # Profile, doesn't exist. Mb has been deleted.
          # Set default profile as active
          self.set_active_profile("default")
    except:
      # Error opening config.json
      # Save default scheme to config file and load default profile
      self.config = self.get_default_config()
      self.config_profile = self.config['profile']['default']      
      self.write_config_to_file(self.config)

  def write_config_to_file(self, c):
    """
    Save config changes to file
    :return:
      1 if succeeded
      0 if failed 
    """
    try:
      with open('config.json', 'w') as f:
        json.dump(self.config, f)
      return 1
    except:
      return 0

  def update_config_profile(self, p, c):
    """
    Write changes in profile to config file
    :return:
      1 if succeeded
      0 if failed 
    """
    try:
      with open('config.json', 'w') as f:
        self.config['profile'][p].update(c)
        json.dump(self.config, f)
      return 1
    except:
      return 0

  def get_default_config(self):
    """
    Default config in case of an error with opening config file
    :return: dictionary with default values
    """
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
    """
    Allows to change config profile (from GUI)

    :param p: profile name
    :return:
      True if succeeded
      False if failed
    """
    
    # Check if profile from parameter exists in config
    if p in self.get_profiles():
      self.config['current_profile'] = p
      # Load new config's values
      self.config_profile = self.config['profile'][p]
      self.write_config_to_file(self.config['profile'])
      return True
    return False

  def create_new_profile(self, name, body):
    """
    Allows to create new profile (from GUI)

    :param name: new profile's name
    :param body: new profile's config values
    :return:
      True if succeeded
      False if failed
    """

    # Check if profile with provided name doesn't already exist
    if name not in self.get_profiles():
      # Get default profile and set new values to it
      blank_body = self.get_default_config()['profile']['default']
      blank_body.update(body)
      self.config['profile'][name] = blank_body
      # Set new profile as current (active)
      self.config['current_profile'] = name
      self.write_config_to_file(self.config)
      return True
    return False

  def get_profiles(self):
    """
    :return: list of all available in config file profile names
    """
    return list(self.config['profile'].keys())

  def rename_profile(self, old, new):
    """
    Allows to rename existing profile

    :param old: old profile name
    :param new: new profile name
    :return:
      True if succeeded
      False if failed
    """

    # Check if such profile exists and
    # if its new name isn't already taken
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
    """
    Allows to delete existing profile
    :param name: name of the profile to be deleted
    :return:
      True if profile deleting succeeded
      False if profile couldn't be deleted
    """

    # Check if provided profile even exists and if
    # its name isn't default. Deleting default profile isn't allowed
    if name not in self.get_profiles() or name == "default":
      return False
    self.config['profile'].pop(name)
    self.write_config_to_file(self.config)
    return True

  def get_output(self):
    """
    Function for GUI interface for displaying messages
    :return:
      - list with all outputs
      - length of that list
    """
    return self.output, len(self.output)

  def check_window_attribute(self):
    """
    Window ID is necessary for this program be running.
    Here we check if Window ID is correct.
    If it's not, we take first available one and save it 
    to config file.
    """
    if "window_id" not in self.config_profile.keys():
      # Missing window ID attribute in config file
      self.output.append(self.outputs['window_id_err'])
    elif (not self.config_profile['window_id'] or 
          not isinstance(self.config_profile['window_id'], int)):
      # Incorrect window ID. May be empty attr value or value not being
      # in correct format (int)
      self.output.append(self.outputs['window_id_err'])

    # If window_id is incorrect, get first correct one and save it
    available_windows = self.get_available_windows()
    window_names = [x for x in available_windows.values()]

    if not str(self.config_profile['window_id']) in available_windows.keys():
      # Window ID is set to window that is not active/open
      self.config_profile['window_id'] = int(list(available_windows.keys())[0])
      self.update_config_profile(self.config['current_profile'], self.config_profile)

  def get_available_windows(self):
    """
    :return: list of all available/active/open windows
    """
    windows = {}
    for title in pygetwindow.getAllTitles():
      # Check if window title is not empty
      if title:
        windows[str(pygetwindow.getWindowsWithTitle(title)[0]._hWnd)] = title
    return windows

  def take_test_screenshot(self):
    """
    Takes single test screenshot.
    Function called from button in GUI.
    """
    self.load_config()
    self.check_window_attribute()
    if (self.take_screenshot(
          self.config_profile['window_id'], 
          self.config_profile['ss_path'], "test") != -1):
      # SS taken successfully
      # Display ss info msg
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
    """
    Runs program main loop (ss taking loop) as a thread
    """
    self.stop = False
    run_thread = threading.Thread(target=self.main_loop)
    run_thread.start()
    
  def stop_program(self):
    """
    Stops program main loop (ss taking loop)
    """
    self.stop = True

  def main_loop(self):
    """
    Main loop. Function taking screenshots.
    """

    # Get the number (name) of the first img after restarting the program
    # We do not want to overrite already taken ss's
    i = self.start_img_number(self.config_profile['ss_path'])
    self.output.append(f"{self.outputs['starting_with']} {i}.jpg")

    # Main loop
    while not self.stop:
      if (self.take_screenshot(
            self.config_profile['window_id'], 
            self.config_profile['ss_path'], str(i)) == -1):
        # Error taking ss. Stop program
        self.stop_program()
        return

      # i > 0 because we want to start comparing img's
      # after the first screenshot was taken
      if i > 0:
        # Get ss's path to later pass them for comparison
        if self.config_profile['ss_path']:
          # Imgs saved in different directory than the main program
          img1 = pathlib.Path(self.config_profile['ss_path']) / (str(i-1) + ".jpg")
          img2 = pathlib.Path(self.config_profile['ss_path']) / (str(i) + ".jpg")
        else:
          # Imgs saved in same directory than the main program
          img1 = str(i-1) + ".jpg"
          img2 = str(i) + ".jpg"

        self.output.append("{} {} {} {} = {:.5f}%"
              .format(self.outputs['diff_between'], 
                      str(i-1) + ".jpg", 
                      self.outputs['and'], 
                      str(i) + ".jpg", 
                      self.percentage_diff_between_two_imgs(img1, img2)
                      ))
        
        # If difference between two images is too small, it means slide wasn't changed
        # We want to delete this image in order not to have img duplicates
        if (self.percentage_diff_between_two_imgs(img1, img2) <
            float(self.config_profile['diff_percentage'])):
          try:
            # Delete duplicate img
            pathlib.Path(img2).unlink()
          except:
            pass
          # Img was duplicate, so dont increase next img's name number
          i -= 1

      time.sleep(self.config_profile['step'])
      i += 1

  def take_screenshot(self, window, path, img_name):
    """ https://stackoverflow.com/a/24352388
    Function taking screenshots of specified window, path and name
    :param window: window handle (window ID)
    :param path: path where the ss is going to be saved
    :param img_name: name of screenshot e.g. "0" means "0.jpg"
    :return:
      -1 if ss couldn't be taken
    """
    hwnd = window
    if hwnd == 0:
      # Window ID can't be equal to 0
      self.output.append(self.outputs['wrong_window_id'])
      return -1
    
    try:
      # Window coords
      left, top, right, bot = win32gui.GetClientRect(hwnd)
    except:
      self.output.append(self.outputs['wrong_window_id'])
      return -1
  
    # Calculate width and height of the window
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

    # Crop image according to the set coordinates
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

    # Create new folder according to set path from config file
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    if path:
      ss_img = pathlib.Path(path) / (img_name + ".jpg")
    else:
      ss_img = img_name + ".jpg"

    if result == 1:
      # SS taken successfully
      im.save(ss_img)

  def percentage_diff_between_two_imgs(self, img1, img2):
    """
    Calculate percentage difference of two imgs
    :return: percentage difference of two imgs. Float number [0.0; 100.0]
    """

    # Check if resolution of both images are the same
    # If not, we can not compare them
    i1, i2 = Image.open(img1), Image.open(img2)
    if not (i1.size == i2.size):
      # Different resolutions
      # Return difference as 100%
      return 100
    return imgcompare.image_diff_percent(i1, i2)

  def start_img_number(self, path):
    """
    As we start program, we don't want to just start
    saving screenshots from like 0.jpg, 1.jpg...
    because they will overwrite any screenshots previously taken.
    This function calculates number of the photo 
    from which we start taking screenshots

    0 <- start with 0.jpg
    
    :param path: path to directory to scan its files
    :return: img number [int]
    """
    img_names = []

    try:
      # List throught all files (ending with ".jpg") in specified directory
      # and save their names (as int) to img_names list
      for file in os.listdir(path):
        if file.endswith(".jpg"):
          if (file.replace(".jpg", "")).isnumeric():
            img_names.append(int(file.replace(".jpg", "")))
    except:
      # No imgs in dir.
      return 0
    
    if img_names:
      # Sort img names and return the largest number increased by 1 
      img_names.sort()
      return img_names[-1] + 1
    else:
      return 0

  def set_ss_coords(self, curr_win_id):
    """
    Sets crop coordinates. 
    Function called from button in GUI.
    
    :param curr_win_id: ID of current (cropped) window 
    """
    
    # Variable to store time of thread start
    global set_coords_thread_start_time
    self.top_left_coords = {}
    self.bottom_right_coords = {}
    self.thread_stop_event = threading.Event()

    # Keyboard listener function
    def on_press(key):
      """
      :return: False - stop listener
      """
      global set_coords_thread_start_time
      
      # F1 - key for Top-Left coords
      if key == keyboard.Key.f1:
        top_left = {
          "x": pg.position()[0],
          "y": pg.position()[1]
        }
        self.top_left_coords = top_left
      # F2 - key for Bottom-Right coords
      elif key == keyboard.Key.f2:
        bottom_right = {
          "x": pg.position()[0],
          "y": pg.position()[1]
        }
        self.bottom_right_coords = bottom_right
      
      # Check time elapsed after thread start
      # If it's > 30 seconds then stop thread
      if key:
        if (time.time() - set_coords_thread_start_time) > 30:
          self.thread_stop_event.set()
          return False # Stop Listener
      
      # ESC - key to cancel setting coords
      if key == keyboard.Key.esc:
        self.thread_stop_event.set()
        return False # Stop Listener
      
      # If both top-left and bottom-right coords were set
      # we want to check their correctness and save them to config file
      if self.top_left_coords and self.bottom_right_coords:
        x1, y1, x2, y2 = win32gui.GetWindowRect(curr_win_id)

        # Check if TOP_LEFT corner is above BOTTOM_RIGHT corner of rectangle
        if not ((self.top_left_coords['x'] < self.bottom_right_coords['x']) and 
                (self.top_left_coords['y'] < self.bottom_right_coords['y'])):
          self.top_left_coords = {}
          self.bottom_right_coords = {}
          self.thread_stop_event.set()
          return False # Stop listener

        # Check if selected coords fit the window area
        if (self.top_left_coords['x'] < x1 or self.bottom_right_coords['x'] > x2 or
            self.top_left_coords['y'] < y1 or self.bottom_right_coords['y'] > y2):
          self.top_left_coords = {}
          self.bottom_right_coords = {}
          self.thread_stop_event.set()
          return False # Stop listener

        # If coords are correct, we want to store window position
        # in order to shift ss area while moving window
        self.config_profile['window_pos']['x'] = x1
        self.config_profile['window_pos']['y'] = y1

        self.config_profile['top_left_coords'] = self.top_left_coords
        self.config_profile['bottom_right_coords'] = self.bottom_right_coords

        # Terminate the thread
        self.thread_stop_event.set()

        return False # Stop listener

    # Create and start keyboard listener
    l1 = keyboard.Listener(on_press=on_press)
    set_coords_thread_start_time = time.time()
    l1.start()

  def get_rel_crop_coords(self, tl_x, tl_y):
    """
    Calculates relative coordinates to crop screenshot.
    (0, 0) absolute means coordinates of screen
    (0, 0) relative means coordinates in window object
    We need relative coordinates cause they allow to crop saved screenshot image 
    
    :return: relative coordinates
      top_left_x, top_left_y, bottom_right_x, bottom_right_y [float, float, float, float]
    """
    tl_mouse_x = self.config_profile.get("top_left_coords").get("x")
    tl_mouse_y = self.config_profile.get("top_left_coords").get("y")
    br_mouse_x = self.config_profile.get("bottom_right_coords").get("x")
    br_mouse_y = self.config_profile.get("bottom_right_coords").get("y")

    # Calculate window movement
    x_shift = tl_x - self.config_profile['window_pos']['x']
    y_shitf = tl_y - self.config_profile['window_pos']['y']

    # Substracting by 8, because
    # it turns out that the topleft window position
    # in Windows is not (0, 0) but (-8, -8)

    # x1, y2 - top left
    x1 = tl_mouse_x - tl_x + x_shift - 8
    y1 = tl_mouse_y - tl_y + y_shitf

    # x2, y2 - bottom right
    x2 = br_mouse_x - tl_x + x_shift - 8
    y2 = br_mouse_y - tl_y + y_shitf

    return x1, y1, x2, y2