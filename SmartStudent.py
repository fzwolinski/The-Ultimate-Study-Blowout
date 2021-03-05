import sys
import json
import pygetwindow

class SmartStudent:
  def __init__(self, flags=[]):
    if len(flags) > 0:
      self.handle_flags(flags)
    self.load_config()

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

  def write_config_to_file(self):
    with open('config.json', 'w') as f:
      json.dump(self.config, f)

  def default_config(self):
    return  {
      "window": "",
      "step": 15,     # Take screenshot every 15s
      "ss_path": "/"
    }

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