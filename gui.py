from tkinter import filedialog
from tkinter import *
from SmartStudent import *
import time
import webbrowser

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600 

MENU_HEIGHT = 26

MAIN_BG = "#fff1e5"

root = Tk()
root.title("SmartStudent")
root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}") 
root.resizable(False,False)

ss_click_time = -2
save_config_click_time = -2

ss = SmartStudent()

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
menu_btns_frame = Frame(root, width=SCREEN_WIDTH, height=MENU_HEIGHT, bg=MAIN_BG)
menu_btns_frame.pack(expand=True, fill=BOTH)

main_home_btn = Button(menu_btns_frame, text="Home", command=set_home_page)
main_config_btn = Button(menu_btns_frame, text="Config", command=set_config_page)
main_info_btn = Button(menu_btns_frame, text="Info", command=set_info_page)

main_home_btn.pack(side=LEFT)
main_config_btn.pack(side=LEFT)
main_info_btn.pack(side=LEFT)
########################################  

# Main Views
home_frame = Frame(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT-MENU_HEIGHT, bg=MAIN_BG)
home_frame.pack()

config_frame = Frame(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT-MENU_HEIGHT, bg=MAIN_BG)
info_frame = Frame(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT-MENU_HEIGHT, bg=MAIN_BG)

main_views = [home_frame, config_frame, info_frame]
############

############ Home Page ############

run_stop = StringVar()
run_stop.set("Run!")
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
    run_stop.set("Stop!")
    ss.run()
    print("Running program")
  else:
    enable_buttons_on_stop()
    run_stop.set("Run!")
    ss.stop_program()
    print("Stopped")
  running = not running

def enable_buttons_on_stop():
  take_screenshot_btn["state"] = "normal"
  main_home_btn["state"] = "normal"
  main_config_btn["state"] = "normal"

def disable_buttons_on_running():
  take_screenshot_btn["state"] = "disable"
  main_home_btn["state"] = "disable"
  main_config_btn["state"] = "disable"


take_screenshot_btn = Button(home_frame, text="Test Screenshot", command=take_screenshot)
take_screenshot_btn.place(relx=0.07, rely=0.1, width=120, height=40)

run_program_btn = Button(home_frame, textvariable=run_stop, command=run_program)
run_program_btn.place(relx=0.5, rely=0.2, anchor=CENTER, width=230, height=70)

output_text = StringVar()

output_label = Label(home_frame, textvariable=output_text, borderwidth=4, relief="ridge", bg="white")
output_label.place(rely=1+0.01 , relx=0.5, height=180, width=SCREEN_WIDTH+8, anchor=S)

###################################

############ Config Page ############
windows = ss.available_windows()
window_names = [x for x in windows.values()]

# Inputs
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
  # Window ID
  if str(ss.config_profile["window_id"]) in windows.keys():
    clicked_window.set(windows[str(ss.config_profile["window_id"])])
  else:
    clicked_window.set(window_names[0])

  # Step
  config_step_entry.delete(0, END)
  config_step_entry.insert(0, ss.config_profile["step"])
  
  # Path
  path.set(ss.config_profile["ss_path"])

  # Percentage difference
  config_diff_perc_entry.delete(0, END)
  config_diff_perc_entry.insert(0, ss.config_profile["diff_percentage"])

  # Crop screenshot
  crop_ss.set(1 if ss.config_profile["crop_img"] else 0)
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
    if ss.update_config_profile(ss.config["current_profile"], new_config):
      save_file_success.set("Saved!")
    else:
      save_file_success.set("Error!")
  # Create new profile
  elif action == "add":
    if ss.create_new_profile(profile_name.get(), new_config):
      display_profiles()
  # Rename profile
  elif action == "rename":
    if ss.rename_profile(ss.config["current_profile"], profile_name.get()):
      hide_profile_name_input()
      display_profiles()



def validate_config():
  correct_values = True
  try:
    step = int(config_step_entry.get())
    if step > 0:
      step_validate.set("Good")
    else:
      step_validate.set("Wrong Value!")
  except:
    step_validate.set("Wrong Value!")
    correct_values = False

  try:
    diff_perc = float(config_diff_perc_entry.get())
    if diff_perc >= 0 and diff_perc <= 100:
      diff_perc_validate.set("Good")
    else:
      diff_perc_validate.set("Wrong Value!")
  except:
    diff_perc_validate.set("Wrong Value!")
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
    coords_validate.set("Good")
    coords_tl.set(str(coord_top_left))
    coords_br.set(str(coord_bottom_right))
  except:
    coords_validate.set("Not set")


config_window_id_label = Label(config_frame, text="Window ID").place(relx=0.05, rely=0.08)
config_window_id_op_menu = OptionMenu(config_frame, clicked_window, *window_names)
config_window_id_op_menu.place(relx=0.28, rely=0.08)

config_step_label = Label(config_frame, text="Step").place(relx=0.05, rely=0.08+0.08)
config_step_entry = Entry(config_frame)
config_step_entry.place(relx=0.28, rely=0.08+0.08)
config_step_validate_label = Label(config_frame, textvariable=step_validate).place(relx=0.43, rely=0.08+0.08)

config_ss_path_label = Label(config_frame, text="Path").place(relx=0.05, rely=0.08+0.08+0.08)
config_ss_path_entry = Button(config_frame, text="Select Path!", command=set_path)
config_ss_path_entry.place(relx=0.28, rely=0.08+0.08+0.08)

config_ss_current_path_label = Label(config_frame, textvariable=path).place(relx=0.43, rely=0.08+0.08+0.08)

config_diff_perc_label = Label(config_frame, text="Percentage difference  [0.0; 100.0]").place(relx=0.05, rely=0.08+0.08+0.08+0.08)
config_diff_perc_entry = Entry(config_frame)
config_diff_perc_entry.place(relx=0.28, rely=0.08+0.08+0.08+0.08)
config_diff_perc_validate_label = Label(config_frame, textvariable=diff_perc_validate).place(relx=0.43, rely=0.08+0.08+0.08+0.08)

config_ss_coords_label = Label(config_frame, text="Crop Screenshot").place(relx=0.05, rely=0.08+0.08+0.08+0.08+0.08)
config_ss_coords_checkbutton = Checkbutton(config_frame, text="Crop", variable=crop_ss).place(relx=0.18, rely=0.08+0.08+0.08+0.08+0.08)
config_ss_coords_button = Button(config_frame, text="Set Crop Coords!", command=set_ss_coords).place(relx=0.28, rely=0.08+0.08+0.08+0.08+0.08)
config_ss_coords_validate_label = Label(config_frame, textvariable=coords_validate).place(relx=0.43, rely=0.08+0.08+0.08+0.08+0.08)
config_ss_current_coords_tl_label = Label(config_frame, textvariable=coords_tl).place(relx=0.55, rely=0.08+0.08+0.08+0.08+0.08)
config_ss_current_coords_br_label = Label(config_frame, textvariable=coords_br).place(relx=0.68, rely=0.08+0.08+0.08+0.08+0.08)

config_save = Button(config_frame, text="Save", command=lambda action="save": save_config(action))
config_save.place(relx=0.28, rely=0.08+0.08+0.08+0.08+0.08+0.08+0.08+0.08)

profile_name = Entry(config_frame)

save_file_success_info = Label(config_frame, textvariable=save_file_success).place(relx=0.28, rely=0.08+0.08+0.08+0.08+0.08+0.08+0.08+0.08+0.08+0.08)




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
  show_profile_name_input("Profile name")
  config_save.configure(command=lambda action="add": save_config(action))
"""
config_profiles = list(ss.config["profile"].keys())
profile_button = [None] * (len(config_profiles) + 1)

i = 0.08
for j in range(len(config_profiles)):
  profile_button[j] = Button(config_frame, text=config_profiles[j], command=lambda p=config_profiles[j]: set_profile(p))
  profile_button[j].place(rely=i, relx=1, anchor=E)
  i += 0.046

profile_button[j+1] = Button(config_frame, text="+", command=new_profile_form)
profile_button[j+1].place(rely=i+0.05, relx=1, anchor=E)

def display_profiles():
  global profile_button
  #print(profile_button[0])
  for j in range(len(profile_button)):
    profile_button[j].place_forget()
    print(j)
  
  config_profiles = list(ss.config["profile"].keys())
  profile_button = [None] * (len(config_profiles) + 1)

  i = 0.08
  for j in range(len(config_profiles)):
    profile_button[j] = Button(config_frame, text=config_profiles[j], command=lambda p=config_profiles[j]: set_profile(p))
    profile_button[j].place(rely=i, relx=1, anchor=E)
    i += 0.046

  profile_button[j+1] = Button(config_frame, text="+", command=new_profile_form)
  profile_button[j+1].place(rely=i+0.05, relx=1, anchor=E)
"""

profile_button = []

def display_profiles():
  global profile_button
  
  if profile_button:
    for p in profile_button:
      p.place_forget()
      
  profile_button.clear()

  config_profiles = list(ss.config["profile"].keys())

  i = 0.18
  for j in range(len(config_profiles)):
    profile_button.append(Button(config_frame, text=config_profiles[j], command=lambda p=config_profiles[j]: set_profile(p)))
    profile_button[j].place(rely=i, relx=1, anchor=E)
    i += 0.046

  add_profile_button = Button(config_frame, text="+", command=new_profile_form)
  add_profile_button.place(rely=0.08, relx=1, anchor=E)
  
def rename_profile():
  show_profile_name_input(ss.config["current_profile"])
  config_save.configure(command=lambda action="rename": save_config(action))

def delete_profile():
  if ss.delete_profile(ss.config["current_profile"]):
    display_profiles()
    set_profile((ss.get_profiles())[0])


rename_profile = Button(config_frame, text="Rename Profile", command=rename_profile).place(relx=1, rely=1, anchor=SE)
delete_profile = Button(config_frame, text="Delete Profile", command=delete_profile).place(relx=1, rely=0.955, anchor=SE)


###################################

############ Info Page ############
def open_url(url):
  webbrowser.open_new(url)

info_author_label = Label(info_frame, text="Author", font=("Arial", 35), bg=MAIN_BG).place(relx=0.5, rely=0.2, anchor=CENTER)
info_author_link_label = Label(info_frame, text="Github", cursor="hand2", font="Arial 20 underline", bg=MAIN_BG, fg="#0645AD")
info_author_link_label.place(relx=0.5, rely=0.4, anchor=CENTER)
info_author_link_label.bind("<Button-1>", lambda e: open_url("https://github.com/fzwolinski"))

###################################

def on_window_close():
  ss.stop_program()
  root.destroy()

root.protocol("WM_DELETE_WINDOW", on_window_close)
root.mainloop()