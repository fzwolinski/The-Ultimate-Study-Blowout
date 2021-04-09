from tkinter import filedialog
from tkinter import *
from tkinter import font as tkFont
from TUSB import *
import json
import time
import webbrowser
import threading

tusb = TUSB()

# All gui texts in specified lang
gui_texts = {}

# Load translation
with open(f"langs/{tusb.config['lang']}.json") as f:
  gui_texts = json.load(f)['gui']

# Load theme
with open(f"themes/{tusb.config['theme']}.json") as f:
  theme = json.load(f)


SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600 
MENU_HEIGHT = 26

root = Tk()
root.title("SmartStudent")
root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}") 
root.resizable(False,False)

# Timer variable to allow taking ss's no more than once every 2 sec
ss_click_time = -2

# Timer variable to allow saving config no more than once every 2 sec
save_config_click_time = -2

# Controls output update loop
# Set to True, breaks infinite loop 
exit_program = False

# Change Main View
def set_home_page():
  """
  Sets main view to Home page
  """
  set_main_view(home_frame)

def set_config_page():
  """
  Sets main view to Config page
  """
  set_main_view(config_frame)
  clear_config_status()
  insert_config_values()
  display_profiles()

def set_desc_page():
  """
  Sets main view to Description page
  """
  set_main_view(desc_frame)

def set_info_page():
  """
  Sets main view to Info page
  """
  set_main_view(info_frame)

def set_main_view(p):
  """
  Allows to set current main view
  Hides other views and load "p" (from parameter) view
  
  :param p: view to be set
  """
  for view in main_views:
    if view != p:
      view.pack_forget()
  p.pack()

################# Menu #################
menu_btns_frame = Frame(
  root, 
  width=SCREEN_WIDTH, 
  height=MENU_HEIGHT, 
  bg=theme['MAIN_BG']
)
menu_btns_frame.pack(expand=True, fill=BOTH)

main_home_btn = Button(
  menu_btns_frame, 
  text=gui_texts['home'], 
  command=set_home_page, 
  bg=theme['MENU_BTN_BG'], 
  activebackground=theme['ACTIVE_MENU_BTN_BG'], 
  cursor=theme["CURSOR_ON_HOVER"]
)
main_config_btn = Button(
  menu_btns_frame, 
  text=gui_texts['config'],
  command=set_config_page, 
  bg=theme['MENU_BTN_BG'], 
  activebackground=theme['ACTIVE_MENU_BTN_BG'], 
  cursor=theme["CURSOR_ON_HOVER"]
)
main_description_btn = Button(
  menu_btns_frame, 
  text=gui_texts['desc'], 
  command=set_desc_page, 
  bg=theme['MENU_BTN_BG'], 
  activebackground=theme['ACTIVE_MENU_BTN_BG'], 
  cursor=theme["CURSOR_ON_HOVER"]
)
main_info_btn = Button(
  menu_btns_frame, 
  text=gui_texts['info'], 
  command=set_info_page, 
  bg=theme['MENU_BTN_BG'], 
  activebackground=theme['ACTIVE_MENU_BTN_BG'], 
  cursor=theme["CURSOR_ON_HOVER"]
)

main_home_btn.pack(side=LEFT)
main_config_btn.pack(side=LEFT)
main_description_btn.pack(side=LEFT)
main_info_btn.pack(side=LEFT)
########################################  

############## Main Views ##############
home_frame = Frame(
  root, 
  width=SCREEN_WIDTH, 
  height=SCREEN_HEIGHT-MENU_HEIGHT, 
  bg=theme['MAIN_BG']
)
home_frame.pack()

config_frame = Frame(
  root, 
  width=SCREEN_WIDTH, 
  height=SCREEN_HEIGHT-MENU_HEIGHT, 
  bg=theme['MAIN_BG']
)
desc_frame = Frame(
  root, 
  width=SCREEN_WIDTH, 
  height=SCREEN_HEIGHT-MENU_HEIGHT, 
  bg=theme['MAIN_BG']
)
info_frame = Frame(
  root, 
  width=SCREEN_WIDTH, 
  height=SCREEN_HEIGHT-MENU_HEIGHT, 
  bg=theme['MAIN_BG']
)

# list of all available main views
main_views = [home_frame, config_frame, desc_frame, info_frame]
########################################

############ Home Page ############

# Text of button running and stopping program
run_stop = StringVar()
run_stop.set(f"{gui_texts['run_program']}!")
# Tells if program is running or not
running = False

def take_screenshot():
  """
  Calls take screenshot method
  """
  # Prevent button spam by limiting up to once per 2 sec
  global ss_click_time
  if (time.perf_counter() - ss_click_time) > 2:
    ss_click_time = time.perf_counter()
    tusb.take_test_screenshot()

def run_program():
  """
  Run / Stop program button
  """
  global running
  if not running:
    # If not running, run it
    
    # Make all btns not clickable
    disable_buttons_on_running()
    run_stop.set(gui_texts['stop_program'])
    run_program_btn.configure(
      bg=theme['STOP_PROGRAM_BTN_BG'], 
      activebackground=theme['STOP_PROGRAM_BTN_BG'], 
      fg=theme['STOP_PROGRAM_BTN_FG']
    )
    # Run main program loop
    tusb.run()
    # Extend output field
    output_text.place(
      rely=1+0.01, 
      relx=0.5, 
      height=400, 
      width=SCREEN_WIDTH+1, 
      anchor=S
    )
  else:
    # If running, stop it
    enable_buttons_on_stop()
    run_stop.set(f"{gui_texts['run_program']}!")
    run_program_btn.configure(
      bg=theme['RUN_PROGRAM_BTN_BG'], 
      activebackground=theme['RUN_PROGRAM_BTN_BG'], 
      fg=theme['RUN_PROGRAM_BTN_FG']
    )
    # Stop main program loop
    tusb.stop_program()
    # Shrink output field
    output_text.place(
      rely=1+0.01, 
      relx=0.5, 
      height=180, 
      width=SCREEN_WIDTH+1, 
      anchor=S
    )
  # Switch running status to opposite
  running = not running

def enable_buttons_on_stop():
  """
  Makes buttons enabled (clickable)
  """
  take_screenshot_btn['state'] = "normal"
  main_home_btn['state'] = "normal"
  main_config_btn['state'] = "normal"
  main_info_btn['state'] = "normal"

def disable_buttons_on_running():
  """
  Makes buttons disabled (un-clickable)
  """
  take_screenshot_btn['state'] = "disable"
  main_home_btn['state'] = "disable"
  main_config_btn['state'] = "disable"
  main_info_btn['state'] = "disable"

take_screenshot_btn = Button(
  home_frame, 
  text=gui_texts['test_screenshot'], 
  command=take_screenshot, 
  font=theme['TEST_SS_BTN_FONT'], 
  bg=theme['TEST_SS_BTN_BG'], 
  activebackground=theme['ACTIVE_TEST_SS_BTN_BG'], 
  fg=theme['TEST_SS_BTN_FG'], 
  cursor=theme["CURSOR_ON_HOVER"]
)
take_screenshot_btn.place(relx=0.07, rely=0.1, width=140, height=50)

run_program_btn = Button(
  home_frame, 
  textvariable=run_stop, 
  command=run_program, 
  font=theme['RUN_PROGRAM_BTN_FONT'], 
  bg=theme['RUN_PROGRAM_BTN_BG'], 
  activebackground=theme['RUN_PROGRAM_BTN_BG'], 
  fg=theme['RUN_PROGRAM_BTN_FG'], 
  cursor=theme["CURSOR_ON_HOVER"]
)
run_program_btn.place(relx=0.5, rely=0.2, anchor=CENTER, width=230, height=70)

output_text = Text(
  home_frame, 
  padx=10, 
  pady=10, 
  bg=theme['OUTPUT_TEXT_BG'], 
  fg=theme['OUTPUT_TEXT_FG']
)
output_text.place(rely=1+0.01 , relx=0.5, height=180, width=SCREEN_WIDTH+1, anchor=S)

# Current length of output
output_widget_len = 0

def update_output():
  """
  Shows all outputs in output field
  """
  global output_widget_len
  
  while not exit_program:
    # get output, and output lenght from class object
    output, out_len = tusb.get_output()
    # set output field "insertable"
    output_text.config(state=NORMAL)
    
    # Insert all the outputs that aren't inserted yet
    # by comparing current output lenght with output from class obj
    for o in output[output_widget_len : out_len]:
      output_text.insert(END, "- " + o + "\n")

    # Update current output lenght
    output_widget_len = out_len
    # Scroll widget to the very bottom
    output_text.see("end")
    # set output field "not-insertable"
    output_text.config(state=DISABLED)
    
    time.sleep(3)

# Update output field in the background
output_update = threading.Thread(target=update_output)
output_update.setDaemon(True)
output_update.start()

###################################

############ Config Page ############
windows = tusb.get_available_windows()
window_names = [x for x in windows.values()]

langs = tusb.get_available_translations()
themes = tusb.get_available_themes()

# Config inputs
clicked_lang = StringVar()
clicked_theme = StringVar()
clicked_window = StringVar()
path = StringVar()
crop_ss = IntVar()
coords_tl = StringVar()
coords_br = StringVar()

# Validate msg's
step_validate = StringVar()
diff_perc_validate = StringVar()
coords_validate = StringVar()
save_file_success = StringVar()

def insert_config_values():
  """
  Inserts all current config values to config view inputs
  """
  # Language
  clicked_lang.set(tusb.config["lang"])

  # Theme
  clicked_theme.set(tusb.config["theme"])
  
  # Window ID
  if str(tusb.config_profile['window_id']) in windows.keys():
    clicked_window.set(windows[str(tusb.config_profile['window_id'])])
  else:
    clicked_window.set(window_names[0])

  # Step
  config_step_entry.delete(0, END)
  config_step_entry.insert(0, tusb.config_profile['step'])
  
  # Path
  path.set(tusb.config_profile['ss_path'])

  # Percentage difference
  config_diff_perc_entry.delete(0, END)
  config_diff_perc_entry.insert(0, tusb.config_profile['diff_percentage'])

  # Crop screenshot
  crop_ss.set(1 if tusb.config_profile['crop_img'] else 0)
  coords_tl.set(str(tusb.config_profile.get("top_left_coords")))
  coords_br.set(str(tusb.config_profile.get("bottom_right_coords")))

def clear_config_values():
  """
  Clear config inputs
  """
  # Window ID
  clicked_window.set(window_names[0])

  # Step
  config_step_entry.delete(0, END)
  
  # Path
  path.set("")

  # Percentage difference
  config_diff_perc_entry.delete(0, END)
  
  # Crop screenshot
  crop_ss.set(0)
  coords_tl.set("")
  coords_br.set("")

def set_path():
  """
  Prompt path set
  """
  path_dir = filedialog.askdirectory()
  path.set(path_dir)

def save_config(action):
  """
  Saves / Updates config
  Creates new / Renames profile
  
  :return: False if config values are incorrect (config not validated)
  """

  # Prevent button click spam
  # Max once per 2 sec
  global save_config_click_time
  if (time.perf_counter() - save_config_click_time) < 2:
    return
  save_config_click_time = time.perf_counter()

  # Check if config values are correct
  if not validate_config():
    return False
  # New config dict (also may be dict to update config)
  new_config = {
    "window_id": int(list(windows.keys())[list(windows.values()).index(clicked_window.get())]),
    "step": int(config_step_entry.get()),
    "ss_path": path.get(),
    "diff_percentage": float(config_diff_perc_entry.get()),
    "window_pos": tusb.config_profile["window_pos"],
    "top_left_coords": eval(coords_tl.get()),
    "bottom_right_coords": eval(coords_br.get()),
    "crop_img": True if crop_ss.get() else False
  }
  # Save config/profile (Update)
  if action == "save":
    if tusb.update_config_profile(tusb.config['current_profile'], new_config):
      # Profile updated, display success msg
      save_file_success.set(f"{gui_texts['saved']}!")
    else:
      # Profile not updated, display error msg
      save_file_success.set(f"{gui_texts['error']}!")
  # Create new profile
  elif action == "add":
    if tusb.create_new_profile(profile_name.get(), new_config):
      # Update profiles list
      display_profiles()
  # Rename profile
  elif action == "rename":
    if tusb.rename_profile(tusb.config['current_profile'], profile_name.get()):
      hide_profile_name_input()
      # Update profiles list
      display_profiles()

def validate_config():
  """
  Verifies config for correct values

  :return:
    True if config values are correct
    False if config values are incorrect
  """
  correct_values = True
  try:
    # Step must be int and be > 0
    step = int(config_step_entry.get())
    if step > 0:
      step_validate.set(gui_texts['good'])
    else:
      step_validate.set(f"{gui_texts['wrong_value']}!")
      correct_values = False
  except:
    step_validate.set(f"{gui_texts['wrong_value']}!")
    correct_values = False

  try:
    # Percentage difference must be float and be in range [0; 100]
    diff_perc = float(config_diff_perc_entry.get())
    if diff_perc >= 0 and diff_perc <= 100:
      diff_perc_validate.set(gui_texts['good'])
    else:
      diff_perc_validate.set(f"{gui_texts['wrong_value']}!")
      correct_values = False
  except:
    diff_perc_validate.set(f"{gui_texts['wrong_value']}!")
    correct_values = False

  try:
    # Coords must be dictionary type
    tl_coord = eval(coords_tl.get())
    br_coord = eval(coords_br.get())
  except:
    coords_tl.set("{}")
    coords_br.set("{}")

  return correct_values

def clear_config_status():
  """
  Clears config validate messages
  """
  step_validate.set("")
  diff_perc_validate.set("")
  save_file_success.set("")
  coords_validate.set("")

def check_for_coords_thread():
  """
  Every 2 seconds checks if coordinates has been set

  :return: 
    False if coords were set but were incorrect
  """
  global set_coords_thread_time
  # Get current window ID
  current_window_id = int(list(windows.keys())[list(windows.values()).index(clicked_window.get())])
  # Call method to set ss coords
  tusb.set_ss_coords(current_window_id)
  
  # Loop break means coords has been set
  # Doesn't matter if they are correct or incorrect
  # After 30 seconds, stop listening for coords
  while not tusb.thread_stop_event.is_set():
    if (time.time() - set_coords_thread_time) > 30:
      break
    time.sleep(2)
  
  # Set ss coords button back to "clickable"
  config_ss_coords_button['state'] = "normal"
  # Set save config button "clickable"
  config_save['state'] = "normal"
  
  # Check if coords has been set correctly
  # If not, display error message
  if not (tusb.top_left_coords and tusb.bottom_right_coords):
    coords_validate.set(gui_texts['not_set'])
    return False

  # Get correct coords and display them in GUI
  coord_top_left, coord_bottom_right = tusb.top_left_coords, tusb.bottom_right_coords
  coords_validate.set(gui_texts['good'])
  coords_tl.set(str(coord_top_left))
  coords_br.set(str(coord_bottom_right))
  
def set_ss_coords():
  """
  Btn call function
  Starts function checking if coords were set in thread
  """
  global set_coords_thread_time
  try:
    set_coords = threading.Thread(target=check_for_coords_thread)
    set_coords.setDaemon(True)
    set_coords_thread_time = time.time()
    set_coords.start()
    # Disable buttons:
    #   Set ss coords and Save config
    # while setting coordinates in order not to create multiple identical threads
    config_ss_coords_button['state'] = "disable"
    config_save['state'] = "disable"
  except:
    pass

def change_lang(e):
  """
  Calls method to change GUI language

  :param e: lang to be set. e.g "pl", "en"
  """
  tusb.set_language(clicked_lang.get())

def change_theme(t):
  """
  Calls method to change GUI theme

  :param t: theme to be set. e.g "dark", "light"
  """
  tusb.set_theme(clicked_theme.get())

# User Set Language
language_op_menu = OptionMenu(
  config_frame, 
  clicked_lang, 
  *langs, 
  command=change_lang
)
language_op_menu.place(relx=0.75, rely=0.08)
language_op_menu.config(
  bg=theme['CONFIG_BTN_BG'], 
  activebackground=theme['CONFIG_BTN_BG'], 
  highlightthickness=0
)
language_op_menu["menu"].config(
  bg=theme['CONFIG_BTN_BG']
)

# User Set Theme
theme_op_menu = OptionMenu(
  config_frame, 
  clicked_theme, 
  *themes, 
  command=change_theme
)
theme_op_menu.place(relx=0.82, rely=0.08)
theme_op_menu.config(
  bg=theme['CONFIG_BTN_BG'], 
  activebackground=theme['CONFIG_BTN_BG'], 
  highlightthickness=0
)
theme_op_menu["menu"].config(bg=theme['CONFIG_BTN_BG'])

# User Set window ID
config_window_id_label = Label(
  config_frame, 
  text=gui_texts['window_id'], 
  bg=theme['CONFIG_LABEL_BG'], 
  fg=theme['CONFIG_LABEL_FG']
).place(relx=0.05, rely=0.08)
config_window_id_op_menu = OptionMenu(config_frame, clicked_window, *window_names)
config_window_id_op_menu.config(
  bg=theme['CONFIG_BTN_BG'], 
  activebackground=theme['CONFIG_BTN_BG'], 
  highlightthickness=0
)
config_window_id_op_menu["menu"].config(
  bg=theme['CONFIG_BTN_BG']
)
config_window_id_op_menu.place(relx=0.28, rely=0.08)

# User Set Step
config_step_label = Label(
  config_frame, 
  text=gui_texts['step'], 
  bg=theme['CONFIG_LABEL_BG'], 
  fg=theme['CONFIG_LABEL_FG']
).place(relx=0.05, rely=2*0.08)
config_step_entry = Entry(
  config_frame, 
  bg=theme['CONFIG_ENTRY_BG'], 
  fg=theme['CONFIG_ENTRY_FG'], 
  borderwidth = 0
)
config_step_entry.place(relx=0.28, rely=2*0.08)
config_step_validate_label = Label(
  config_frame, 
  textvariable=step_validate, 
  bg=theme['CONFIG_VALIDATE_LBL_BG'], 
  fg=theme['CONFIG_VALIDATE_FG']
).place(relx=0.43, rely=2*0.08)

# User Set Path
config_ss_path_label = Label(
  config_frame, 
  text=gui_texts['path'], 
  bg=theme['CONFIG_LABEL_BG'], 
  fg=theme['CONFIG_LABEL_FG']
).place(relx=0.05, rely=3*0.08)
config_ss_path_entry = Button(
  config_frame, 
  text=f"{gui_texts['select_path']}!", 
  command=set_path, 
  bg=theme['CONFIG_BTN_BG'], 
  activebackground=theme['CONFIG_ACTIVE_BTN_BG'], 
  cursor=theme["CURSOR_ON_HOVER"]
)
config_ss_path_entry.place(relx=0.28, rely=3*0.08)

config_ss_current_path_label = Label(
  config_frame, 
  textvariable=path, 
  bg=theme['CONFIG_CURRENT_LBL_BG'], 
  fg=theme['CONFIG_LABEL_FG']
).place(relx=0.43, rely=3*0.08)

# User Set Percentage Difference
config_diff_perc_label = Label(
  config_frame, 
  text=gui_texts['percentage_diff'],
  bg=theme['CONFIG_LABEL_BG'], 
  fg=theme['CONFIG_LABEL_FG']
).place(relx=0.05, rely=4*0.08)
config_diff_perc_entry = Entry(
  config_frame, 
  bg=theme['CONFIG_ENTRY_BG'], 
  fg=theme['CONFIG_ENTRY_FG'], 
  borderwidth = 0
)
config_diff_perc_entry.place(relx=0.28, rely=4*0.08)
config_diff_perc_validate_label = Label(
  config_frame, 
  textvariable=diff_perc_validate, 
  bg=theme['CONFIG_VALIDATE_LBL_BG'], 
  fg=theme['CONFIG_VALIDATE_FG']
).place(relx=0.43, rely=4*0.08)

# User Set crop image coordinates
config_ss_coords_label = Label(
  config_frame, 
  text=gui_texts['crop_screenshot'], 
  bg=theme['CONFIG_LABEL_BG'], 
  fg=theme['CONFIG_LABEL_FG']
).place(relx=0.05, rely=5*0.08)
config_ss_coords_checkbutton = Checkbutton(
  config_frame, 
  text=gui_texts['crop'], 
  variable=crop_ss, 
  bg=theme['CONFIG_LABEL_BG'], 
  fg=theme['CONFIG_LABEL_FG'], 
  activebackground=theme['CONFIG_LABEL_BG']
).place(relx=0.18, rely=5*0.08)
config_ss_coords_button = Button(
  config_frame, 
  text=f"{gui_texts['set_crop_coords']}!", 
  command=set_ss_coords, 
  bg=theme['CONFIG_BTN_BG'], 
  activebackground=theme['CONFIG_ACTIVE_BTN_BG'], 
  cursor=theme["CURSOR_ON_HOVER"]
)
config_ss_coords_button.place(relx=0.28, rely=5*0.08)
config_ss_coords_validate_label = Label(
  config_frame, 
  textvariable=coords_validate, 
  bg=theme['CONFIG_VALIDATE_LBL_BG'], 
  fg=theme['CONFIG_VALIDATE_FG']
).place(relx=0.28, rely=5*0.08+0.06)
config_ss_current_coords_tl_label = Label(
  config_frame, 
  textvariable=coords_tl, 
  bg=theme['CONFIG_CURRENT_LBL_BG'], 
  fg=theme['CONFIG_LABEL_FG']
).place(relx=0.55, rely=5*0.08)
config_ss_current_coords_br_label = Label(
  config_frame, 
  textvariable=coords_br, 
  bg=theme['CONFIG_CURRENT_LBL_BG'], 
  fg=theme['CONFIG_LABEL_FG']
).place(relx=0.68, rely=5*0.08)

# User Save config
config_save = Button(
  config_frame, 
  text=gui_texts['save'], 
  command=lambda action="save": save_config(action), 
  bg=theme['CONFIG_SAVE_BTN_BG'], 
  activebackground=theme['CONFIG_ACTIVE_SAVE_BTN_BG'], 
  cursor=theme["CURSOR_ON_HOVER"]
)
config_save.place(relx=0.28, rely=8*0.08)

save_file_success_info = Label(
  config_frame, 
  textvariable=save_file_success, 
  bg=theme['CONFIG_VALIDATE_LBL_BG'], 
  fg=theme['CONFIG_LABEL_FG']
).place(relx=0.28, rely=9*0.08)

# User set profile name
profile_name = Entry(
  config_frame, 
  bg=theme['CONFIG_ENTRY_BG'], 
  fg=theme['CONFIG_ENTRY_FG'], 
  borderwidth = 0
)

def show_profile_name_input(text):
  """
  On time while adding new profile,
  display input getting profile name
  
  :param text: profile name text to be inserted into input
  """
  profile_name.place(relx=0.35, rely=8*0.08)
  profile_name.delete(0, END)
  profile_name.insert(0, text)

def hide_profile_name_input():
  """
  Hides profile name input
  """
  profile_name.place_forget()

def highlight_current_profile():
  """
  Changes background of current profile button
  """

  # Loop throught every profile button and
  # change bg of current one
  for p in profile_button:
    if p['text'] == tusb.config["current_profile"]:
      p.configure(bg=theme['CONFIG_CURRENT_PROF_BG'])
    else:
      p.configure(bg=theme['CONFIG_PROF_BG'])

def set_profile(profile):
  """
  Sets profile to be current active
  
  :param profile: profile to be set to active
  """
  tusb.set_active_profile(profile)
  highlight_current_profile()
  hide_profile_name_input()
  # Insert new profiles values into inputs
  insert_config_values()
  # Set Save Button action to "Save"
  config_save.configure(command=lambda action="save": save_config(action))

def new_profile_form():
  """
  Prepares config form for creating new profile by
  - clearing all values
  - displaying input of new profile's name
  """
  clear_config_values()
  show_profile_name_input(gui_texts['profile_name'])
  
  # Set Save Button action to "Add new profile"
  config_save.configure(command=lambda action="add": save_config(action))

# Buttons of all available profiles
profile_button = []

def display_profiles():
  """
  Updates displayed list of available profiles buttons
  """
  global profile_button
  
  # Hide curretly displaying profile buttons
  if profile_button:
    for p in profile_button:
      p.place_forget()
  
  # Clear list with available profiles
  profile_button.clear()

  # Get all available profiles
  config_profiles = list(tusb.config['profile'].keys())

  i = 0.18 # i = "y" position of button
  # Loop throught all available profiles and display them
  for j in range(len(config_profiles)):
    profile_button.append(Button(
      config_frame, 
      text=config_profiles[j], 
      command=lambda p=config_profiles[j]: set_profile(p), 
      bg=theme['CONFIG_PROF_BG'], 
      activebackground=theme['CONFIG_ACTIVE_PROF_BG'], 
      cursor=theme["CURSOR_ON_HOVER"])
      )
    profile_button[j].place(rely=i, relx=1, anchor=E)
    # Increase "y" position of every btn
    i += 0.046

  # Add new profile button
  add_profile_button = Button(
    config_frame, 
    text=u"\u2795", 
    command=new_profile_form, 
    bg=theme['CONFIG_ADD_PROF_BG'], 
    activebackground=theme['CONFIG_ACTIVE_ADD_PROF_BG'], 
    cursor=theme["CURSOR_ON_HOVER"]
  )
  add_profile_button.place(rely=0.08, relx=1, anchor=E)
  # Change bg of currently active profile
  highlight_current_profile()
  
def rename_profile():
  """
  Displays profile name input and 
  changes "Save profile" btn action to "Rename profile" 
  """
  show_profile_name_input(tusb.config['current_profile'])
  config_save.configure(command=lambda action="rename": save_config(action))

def delete_profile():
  """
  Calls deleting profile method
  """
  if tusb.delete_profile(tusb.config['current_profile']):
    # Display available profiles after delete
    display_profiles()
    # Set first available profile as active
    set_profile((tusb.get_profiles())[0])

rename_profile = Button(
  config_frame, 
  text=gui_texts['rename_profile'], 
  command=rename_profile, 
  bg=theme['CONFIG_RENAME_PROGILE_BTN_BG'], 
  activebackground=theme['CONFIG_ACTIVE_RENAME_PROGILE_BTN_BG'], 
  cursor=theme["CURSOR_ON_HOVER"]
).place(relx=1, rely=1, anchor=SE)

delete_profile = Button(
  config_frame, 
  text=gui_texts['delete_profile'], 
  command=delete_profile, 
  bg=theme['CONFIG_DEL_PROFILE_BTN_BG'], 
  activebackground=theme['CONFIG_ACTIVE_DEL_PROFILE_BTN_BG'], 
  cursor=theme["CURSOR_ON_HOVER"]
).place(relx=1, rely=0.955, anchor=SE)

###################################

############ Description Page ############
DESC_LBL_X = 0.25
DESC_LBL_Y = 0.10

DESC_LBL_FONT = ("Arial", 13)

DESC_WHAT_LBL_X = 0.3
DESC_WHAT_LBL_FONT = ("Arial", 10)

desc_window_id_lbl = Label(
  desc_frame, 
  text=gui_texts['window_id'], 
  font=DESC_LBL_FONT, 
  bg=theme['DESC_LBL_BG'], 
  fg=theme['DESC_LBL_FG']
).place(relx=DESC_LBL_X, rely=DESC_LBL_Y, anchor=E)
desc_step_lbl = Label(
  desc_frame, 
  text=gui_texts['step'], 
  font=DESC_LBL_FONT, 
  bg=theme['DESC_LBL_BG'], 
  fg=theme['DESC_LBL_FG']
).place(relx=DESC_LBL_X, rely=DESC_LBL_Y + 1*0.18, anchor=E)
desc_path_lbl = Label(
  desc_frame, 
  text=gui_texts['path'], 
  font=DESC_LBL_FONT, 
  bg=theme['DESC_LBL_BG'], 
  fg=theme['DESC_LBL_FG']
).place(relx=DESC_LBL_X, rely=DESC_LBL_Y + 2*0.18, anchor=E)
desc_diff_perc_lbl = Label(
  desc_frame, 
  text=gui_texts['percentage_diff'], 
  font=DESC_LBL_FONT, 
  bg=theme['DESC_LBL_BG'], 
  fg=theme['DESC_LBL_FG']
).place(relx=DESC_LBL_X, rely=DESC_LBL_Y + 3*0.18, anchor=E)
desc_coords_lbl = Label(
  desc_frame, 
  text=gui_texts['crop_screenshot'], 
  font=DESC_LBL_FONT, 
  bg=theme['DESC_LBL_BG'], 
  fg=theme['DESC_LBL_FG']
).place(relx=DESC_LBL_X, rely=DESC_LBL_Y + 4*0.18, anchor=E)

desc_what_window_id_lbl = Label(
  desc_frame, 
  text=gui_texts['desc_what_window_id'], 
  font=DESC_WHAT_LBL_FONT, 
  bg=theme['DESC_WHAT_LBL_BG'], 
  fg=theme['DESC_WHAT_LBL_FG']
).place(relx=DESC_WHAT_LBL_X, rely=DESC_LBL_Y, anchor=W)
desc_what_step_lbl = Label(
  desc_frame, 
  text=gui_texts['desc_what_step'], 
  font=DESC_WHAT_LBL_FONT, 
  bg=theme['DESC_WHAT_LBL_BG'], 
  fg=theme['DESC_WHAT_LBL_FG'
], justify=LEFT).place(relx=DESC_WHAT_LBL_X, rely=DESC_LBL_Y + 1*0.18, anchor=W)
desc_what_path_lbl = Label(
  desc_frame, 
  text=gui_texts['desc_what_path'], 
  font=DESC_WHAT_LBL_FONT, 
  bg=theme['DESC_WHAT_LBL_BG'], 
  fg=theme['DESC_WHAT_LBL_FG'
], justify=LEFT).place(relx=DESC_WHAT_LBL_X, rely=DESC_LBL_Y + 2*0.18, anchor=W)
desc_what_diff_perc_lbl = Label(
  desc_frame, 
  text=gui_texts['desc_what_diff_perc'], 
  font=DESC_WHAT_LBL_FONT, 
  bg=theme['DESC_WHAT_LBL_BG'], 
  fg=theme['DESC_WHAT_LBL_FG'
], justify=LEFT).place(relx=DESC_WHAT_LBL_X, rely=DESC_LBL_Y + 3*0.18, anchor=W)
desc_what_coords_lbl = Label(
  desc_frame, 
  text=gui_texts['desc_what_coords'], 
  font=DESC_WHAT_LBL_FONT, 
  bg=theme['DESC_WHAT_LBL_BG'], 
  fg=theme['DESC_WHAT_LBL_FG'
], justify=LEFT).place(relx=DESC_WHAT_LBL_X, rely=DESC_LBL_Y + 4*0.18, anchor=W)

##########################################

############ Info Page ############
def open_url(url):
  """
  Opens url in browser

  :param url: url to be opened
  """
  webbrowser.open_new(url)

info_author_label = Label(
  info_frame, 
  text=gui_texts['author'], 
  font=("Arial", 35), 
  bg=theme['MAIN_BG'], 
  fg=theme['INFO_AUTHOR_LBL_FG']
).place(relx=0.5, rely=0.2, anchor=CENTER)
info_author_link_label = Label(
  info_frame, 
  text="Github", 
  cursor="hand2", 
  font="Arial 20 underline", 
  bg=theme['MAIN_BG'], 
  fg=theme['INFO_AUTHOR_LINK_LBL_FG']
)
info_author_link_label.place(relx=0.5, rely=0.4, anchor=CENTER)
info_author_link_label.bind("<Button-1>", lambda e: open_url("https://github.com/fzwolinski"))

###################################

def on_window_close():
  """
  Clearing on program exit
  Stops main program loop and destroys GUI root object
  """
  exit_program = True
  tusb.stop_program()
  root.destroy()

# Before window close, call on_window_close() function
root.protocol("WM_DELETE_WINDOW", on_window_close)
root.mainloop()