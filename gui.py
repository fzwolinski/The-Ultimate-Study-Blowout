from tkinter import filedialog
from tkinter import *
from tkinter import font as tkFont
from SmartStudent import *
import json
import time
import webbrowser
import threading


ss = SmartStudent()

gui_texts = {}

# Load translation
with open(f"langs/{ss.config['lang']}.json") as f:
  gui_texts = json.load(f)['gui']

# Load theme
with open(f"themes/{ss.config['theme']}.json") as f:
  theme = json.load(f)


SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600 

MENU_HEIGHT = 26

exit_program = False

root = Tk()
root.title("SmartStudent")
root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}") 
root.resizable(False,False)

ss_click_time = -2
save_config_click_time = -2



# Change Main View
def set_home_page():
  set_main_view(home_frame)

def set_config_page():
  set_main_view(config_frame)
  clear_config_status()
  insert_config_values()
  display_profiles()


def set_info_page():
  set_main_view(info_frame)

def set_main_view(p):
  for view in main_views:
    if view != p:
      view.pack_forget()
  p.pack()

################# Menu #################
menu_btns_frame = Frame(root, width=SCREEN_WIDTH, height=MENU_HEIGHT, bg=theme['MAIN_BG'])
menu_btns_frame.pack(expand=True, fill=BOTH)

main_home_btn = Button(menu_btns_frame, text=gui_texts['home'], command=set_home_page, bg=theme['MENU_BTN_BG'], activebackground=theme['ACTIVE_MENU_BTN_BG'])
main_config_btn = Button(menu_btns_frame, text=gui_texts['config'], command=set_config_page, bg=theme['MENU_BTN_BG'], activebackground=theme['ACTIVE_MENU_BTN_BG'])
main_info_btn = Button(menu_btns_frame, text=gui_texts['info'], command=set_info_page, bg=theme['MENU_BTN_BG'], activebackground=theme['ACTIVE_MENU_BTN_BG'])

main_home_btn.pack(side=LEFT)
main_config_btn.pack(side=LEFT)
main_info_btn.pack(side=LEFT)
########################################  

# Main Views
home_frame = Frame(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT-MENU_HEIGHT, bg=theme['MAIN_BG'])
home_frame.pack()

config_frame = Frame(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT-MENU_HEIGHT, bg=theme['MAIN_BG'])
info_frame = Frame(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT-MENU_HEIGHT, bg=theme['MAIN_BG'])

main_views = [home_frame, config_frame, info_frame]
############

############ Home Page ############

run_stop = StringVar()
run_stop.set(f"{gui_texts['run_program']}!")
running = False

def take_screenshot():
  global ss_click_time
  if (time.perf_counter() - ss_click_time) > 2:
    ss_click_time = time.perf_counter()
    ss.take_test_screenshot()

def run_program():
  global running
  if not running:
    disable_buttons_on_running()
    run_stop.set(gui_texts['stop_program'])
    run_program_btn.configure(bg=theme['STOP_PROGRAM_BTN_BG'], activebackground=theme['STOP_PROGRAM_BTN_BG'], fg=theme['STOP_PROGRAM_BTN_FG'])
    ss.run()
    output_text.place(rely=1+0.01 , relx=0.5, height=400, width=SCREEN_WIDTH+1, anchor=S)
  else:
    enable_buttons_on_stop()
    run_stop.set(f"{gui_texts['run_program']}!")
    run_program_btn.configure(bg=theme['RUN_PROGRAM_BTN_BG'], activebackground=theme['RUN_PROGRAM_BTN_BG'], fg=theme['RUN_PROGRAM_BTN_FG'])
    ss.stop_program()
    output_text.place(rely=1+0.01 , relx=0.5, height=180, width=SCREEN_WIDTH+1, anchor=S)
  running = not running

def enable_buttons_on_stop():
  take_screenshot_btn['state'] = "normal"
  main_home_btn['state'] = "normal"
  main_config_btn['state'] = "normal"
  main_info_btn['state'] = "normal"

def disable_buttons_on_running():
  take_screenshot_btn['state'] = "disable"
  main_home_btn['state'] = "disable"
  main_config_btn['state'] = "disable"
  main_info_btn['state'] = "disable"


take_screenshot_btn = Button(home_frame, text=gui_texts['test_screenshot'], command=take_screenshot, font=theme['TEST_SS_BTN_FONT'], bg=theme['TEST_SS_BTN_BG'], activebackground=theme['ACTIVE_TEST_SS_BTN_BG'], fg=theme['TEST_SS_BTN_FG'])
take_screenshot_btn.place(relx=0.07, rely=0.1, width=140, height=50)

run_program_btn = Button(home_frame, textvariable=run_stop, command=run_program, font=theme['RUN_PROGRAM_BTN_FONT'], bg=theme['RUN_PROGRAM_BTN_BG'], activebackground=theme['RUN_PROGRAM_BTN_BG'], fg=theme['RUN_PROGRAM_BTN_FG'])
run_program_btn.place(relx=0.5, rely=0.2, anchor=CENTER, width=230, height=70)

output_text = Text(home_frame, padx=10, pady=10, bg=theme['OUTPUT_TEXT_BG'], fg=theme['OUTPUT_TEXT_FG'])
output_text.place(rely=1+0.01 , relx=0.5, height=180, width=SCREEN_WIDTH+1, anchor=S)

output_widget_len = 0

def update_output():
  global output_widget_len
  
  while not exit_program:
    output, out_len = ss.get_output()    
    output_text.config(state=NORMAL)
    
    for o in output[output_widget_len : out_len]:
      output_text.insert(END, "- " + o + "\n")  

    output_widget_len = out_len
    output_text.see("end")
    output_text.config(state=DISABLED)
    
    time.sleep(3)

output_update = threading.Thread(target=update_output)
output_update.setDaemon(True)
output_update.start()

###################################

############ Config Page ############
windows = ss.available_windows()
window_names = [x for x in windows.values()]

langs = ss.get_available_translations()
themes = ss.get_available_themes()

# Inputs
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
  # Language
  clicked_lang.set(ss.config["lang"])

  # Theme
  clicked_theme.set(ss.config["theme"])
  
  # Window ID
  if str(ss.config_profile['window_id']) in windows.keys():
    clicked_window.set(windows[str(ss.config_profile['window_id'])])
  else:
    clicked_window.set(window_names[0])

  # Step
  config_step_entry.delete(0, END)
  config_step_entry.insert(0, ss.config_profile['step'])
  
  # Path
  path.set(ss.config_profile['ss_path'])

  # Percentage difference
  config_diff_perc_entry.delete(0, END)
  config_diff_perc_entry.insert(0, ss.config_profile['diff_percentage'])

  # Crop screenshot
  crop_ss.set(1 if ss.config_profile['crop_img'] else 0)
  coords_tl.set(str(ss.config_profile.get("top_left_coords")))
  coords_br.set(str(ss.config_profile.get("bottom_right_coords")))

def clear_config_values():
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
  path_dir = filedialog.askdirectory()
  path.set(path_dir)

def save_config(action):
  global save_config_click_time
  if (time.perf_counter() - save_config_click_time) < 2:
    return
  save_config_click_time = time.perf_counter()

  if not validate_config():
    return False
  new_config = {
    "window_id": int(list(windows.keys())[list(windows.values()).index(clicked_window.get())]),
    "step": int(config_step_entry.get()),
    "ss_path": path.get(),
    "diff_percentage": float(config_diff_perc_entry.get()),
    "top_left_coords": eval(coords_tl.get()),
    "bottom_right_coords": eval(coords_br.get()),
    "crop_img": True if crop_ss.get() else False
  }
  # Save config/profile (Update)
  if action == "save":
    if ss.update_config_profile(ss.config['current_profile'], new_config):
      save_file_success.set(f"{gui_texts['saved']}!")
    else:
      save_file_success.set(f"{gui_texts['error']}!")
  # Create new profile
  elif action == "add":
    if ss.create_new_profile(profile_name.get(), new_config):
      display_profiles()
  # Rename profile
  elif action == "rename":
    if ss.rename_profile(ss.config['current_profile'], profile_name.get()):
      hide_profile_name_input()
      display_profiles()



def validate_config():
  correct_values = True
  try:
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
    tl_coord = eval(coords_tl.get())
    br_coord = eval(coords_br.get())
  except:
    coords_tl.set("{}")
    coords_br.set("{}")

  return correct_values

def clear_config_status():
    step_validate.set("")
    diff_perc_validate.set("")
    save_file_success.set("")
    coords_validate.set("")

def set_ss_coords():
  try:
    current_window_id = int(list(windows.keys())[list(windows.values()).index(clicked_window.get())])
    coord_top_left, coord_bottom_right = ss.set_ss_coords(current_window_id)
    coords_validate.set(gui_texts['good'])
    coords_tl.set(str(coord_top_left))
    coords_br.set(str(coord_bottom_right))
  except:
    coords_validate.set(gui_texts['not_set'])

def change_lang(e):
  ss.set_language(clicked_lang.get())

def change_theme(t):
  ss.set_theme(clicked_theme.get())

language_op_menu = OptionMenu(config_frame, clicked_lang, *langs, command=change_lang)
language_op_menu.place(relx=0.75, rely=0.08)
language_op_menu.config(bg=theme['CONFIG_BTN_BG'], activebackground=theme['CONFIG_BTN_BG'], highlightthickness=0)
language_op_menu["menu"].config(bg=theme['CONFIG_BTN_BG'])

theme_op_menu = OptionMenu(config_frame, clicked_theme, *themes, command=change_theme)
theme_op_menu.place(relx=0.82, rely=0.08)
theme_op_menu.config(bg=theme['CONFIG_BTN_BG'], activebackground=theme['CONFIG_BTN_BG'], highlightthickness=0)
theme_op_menu["menu"].config(bg=theme['CONFIG_BTN_BG'])

config_window_id_label = Label(config_frame, text=gui_texts['window_id'], bg=theme['CONFIG_LABEL_BG'], fg=theme['CONFIG_LABEL_FG']).place(relx=0.05, rely=0.08)
config_window_id_op_menu = OptionMenu(config_frame, clicked_window, *window_names)
config_window_id_op_menu.config(bg=theme['CONFIG_BTN_BG'], activebackground=theme['CONFIG_BTN_BG'], highlightthickness=0)
config_window_id_op_menu["menu"].config(bg=theme['CONFIG_BTN_BG'])
config_window_id_op_menu.place(relx=0.28, rely=0.08)

config_step_label = Label(config_frame, text=gui_texts['step'], bg=theme['CONFIG_LABEL_BG'], fg=theme['CONFIG_LABEL_FG']).place(relx=0.05, rely=0.08+0.08)
config_step_entry = Entry(config_frame, bg=theme['CONFIG_ENTRY_BG'], fg=theme['CONFIG_ENTRY_FG'], borderwidth = 0)
config_step_entry.place(relx=0.28, rely=0.08+0.08)
config_step_validate_label = Label(config_frame, textvariable=step_validate, bg=theme['CONFIG_VALIDATE_LBL_BG'], fg=theme['CONFIG_VALIDATE_FG']).place(relx=0.43, rely=0.08+0.08)

config_ss_path_label = Label(config_frame, text=gui_texts['path'], bg=theme['CONFIG_LABEL_BG'], fg=theme['CONFIG_LABEL_FG']).place(relx=0.05, rely=0.08+0.08+0.08)
config_ss_path_entry = Button(config_frame, text=f"{gui_texts['select_path']}!", command=set_path, bg=theme['CONFIG_BTN_BG'], activebackground=theme['CONFIG_ACTIVE_BTN_BG'])
config_ss_path_entry.place(relx=0.28, rely=0.08+0.08+0.08)

config_ss_current_path_label = Label(config_frame, textvariable=path, bg=theme['CONFIG_CURRENT_LBL_BG'], fg=theme['CONFIG_LABEL_FG']).place(relx=0.43, rely=0.08+0.08+0.08)

config_diff_perc_label = Label(config_frame, text=f"{gui_texts['percentage_diff']}  [0.0; 100.0]", bg=theme['CONFIG_LABEL_BG'], fg=theme['CONFIG_LABEL_FG']).place(relx=0.05, rely=0.08+0.08+0.08+0.08)
config_diff_perc_entry = Entry(config_frame, bg=theme['CONFIG_ENTRY_BG'], fg=theme['CONFIG_ENTRY_FG'], borderwidth = 0)
config_diff_perc_entry.place(relx=0.28, rely=0.08+0.08+0.08+0.08)
config_diff_perc_validate_label = Label(config_frame, textvariable=diff_perc_validate, bg=theme['CONFIG_VALIDATE_LBL_BG'], fg=theme['CONFIG_VALIDATE_FG']).place(relx=0.43, rely=0.08+0.08+0.08+0.08)

config_ss_coords_label = Label(config_frame, text=gui_texts['crop_screenshot'], bg=theme['CONFIG_LABEL_BG'], fg=theme['CONFIG_LABEL_FG']).place(relx=0.05, rely=0.08+0.08+0.08+0.08+0.08)
config_ss_coords_checkbutton = Checkbutton(config_frame, text=gui_texts['crop'], variable=crop_ss, bg=theme['CONFIG_LABEL_BG'], fg=theme['CONFIG_LABEL_FG'], activebackground=theme['CONFIG_LABEL_BG']).place(relx=0.18, rely=0.08+0.08+0.08+0.08+0.08)
config_ss_coords_button = Button(config_frame, text=f"{gui_texts['set_crop_coords']}!", command=set_ss_coords, bg=theme['CONFIG_BTN_BG'], activebackground=theme['CONFIG_ACTIVE_BTN_BG']).place(relx=0.28, rely=0.08+0.08+0.08+0.08+0.08)
config_ss_coords_validate_label = Label(config_frame, textvariable=coords_validate, bg=theme['CONFIG_VALIDATE_LBL_BG'], fg=theme['CONFIG_VALIDATE_FG']).place(relx=0.28, rely=0.08+0.08+0.08+0.08+0.08+0.06)
config_ss_current_coords_tl_label = Label(config_frame, textvariable=coords_tl, bg=theme['CONFIG_CURRENT_LBL_BG'], fg=theme['CONFIG_LABEL_FG']).place(relx=0.55, rely=0.08+0.08+0.08+0.08+0.08)
config_ss_current_coords_br_label = Label(config_frame, textvariable=coords_br, bg=theme['CONFIG_CURRENT_LBL_BG'], fg=theme['CONFIG_LABEL_FG']).place(relx=0.68, rely=0.08+0.08+0.08+0.08+0.08)

config_save = Button(config_frame, text=gui_texts['save'], command=lambda action="save": save_config(action), bg=theme['CONFIG_SAVE_BTN_BG'], activebackground=theme['CONFIG_ACTIVE_SAVE_BTN_BG'])
config_save.place(relx=0.28, rely=0.08+0.08+0.08+0.08+0.08+0.08+0.08+0.08)

profile_name = Entry(config_frame, bg=theme['CONFIG_ENTRY_BG'], fg=theme['CONFIG_ENTRY_FG'], borderwidth = 0)

save_file_success_info = Label(config_frame, textvariable=save_file_success, bg=theme['CONFIG_VALIDATE_LBL_BG'], fg=theme['CONFIG_LABEL_FG']).place(relx=0.28, rely=0.08+0.08+0.08+0.08+0.08+0.08+0.08+0.08+0.08)


def show_profile_name_input(text):
  profile_name.place(relx=0.35, rely=0.08+0.08+0.08+0.08+0.08+0.08+0.08+0.08)
  profile_name.delete(0, END)
  profile_name.insert(0, text)

def hide_profile_name_input():
  profile_name.place_forget()

def set_profile(profile):
  ss.set_active_profile(profile)
  hide_profile_name_input()
  insert_config_values()
  config_save.configure(command=lambda action="save": save_config(action))

def new_profile_form():
  clear_config_values()
  show_profile_name_input(gui_texts['profile_name'])
  config_save.configure(command=lambda action="add": save_config(action))

profile_button = []

def display_profiles():
  global profile_button
  
  if profile_button:
    for p in profile_button:
      p.place_forget()
      
  profile_button.clear()

  config_profiles = list(ss.config['profile'].keys())

  i = 0.18
  for j in range(len(config_profiles)):
    profile_button.append(Button(config_frame, text=config_profiles[j], command=lambda p=config_profiles[j]: set_profile(p), bg=theme['CONFIG_PROF_BG'], activebackground=theme['CONFIG_ACTIVE_PROF_BG']))
    profile_button[j].place(rely=i, relx=1, anchor=E)
    i += 0.046

  add_profile_button = Button(config_frame, text=u"\u2795", command=new_profile_form, bg=theme['CONFIG_ADD_PROF_BG'], activebackground=theme['CONFIG_ACTIVE_ADD_PROF_BG'])
  add_profile_button.place(rely=0.08, relx=1, anchor=E)
  
def rename_profile():
  show_profile_name_input(ss.config['current_profile'])
  config_save.configure(command=lambda action="rename": save_config(action))

def delete_profile():
  if ss.delete_profile(ss.config['current_profile']):
    display_profiles()
    set_profile((ss.get_profiles())[0])


rename_profile = Button(config_frame, text=gui_texts['rename_profile'], command=rename_profile, bg=theme['CONFIG_RENAME_PROGILE_BTN_BG'], activebackground=theme['CONFIG_ACTIVE_RENAME_PROGILE_BTN_BG']).place(relx=1, rely=1, anchor=SE)
delete_profile = Button(config_frame, text=gui_texts['delete_profile'], command=delete_profile, bg=theme['CONFIG_DEL_PROFILE_BTN_BG'], activebackground=theme['CONFIG_ACTIVE_DEL_PROFILE_BTN_BG']).place(relx=1, rely=0.955, anchor=SE)


###################################

############ Info Page ############
def open_url(url):
  webbrowser.open_new(url)

info_author_label = Label(info_frame, text=gui_texts['author'], font=("Arial", 35), bg=theme['MAIN_BG'], fg=theme['INFO_AUTHOR_LBL_FG']).place(relx=0.5, rely=0.2, anchor=CENTER)
info_author_link_label = Label(info_frame, text="Github", cursor="hand2", font="Arial 20 underline", bg=theme['MAIN_BG'], fg=theme['INFO_AUTHOR_LINK_LBL_FG'])
info_author_link_label.place(relx=0.5, rely=0.4, anchor=CENTER)
info_author_link_label.bind("<Button-1>", lambda e: open_url("https://github.com/fzwolinski"))

###################################

def on_window_close():
  exit_program = True
  ss.stop_program()
  root.destroy()

root.protocol("WM_DELETE_WINDOW", on_window_close)
root.mainloop()