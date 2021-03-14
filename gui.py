from tkinter import filedialog
from tkinter import *
from SmartStudent import *
import time

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
  if not home_frame.winfo_ismapped():
    config_frame.pack_forget()
    home_frame.pack()

def set_config_page():
  if not config_frame.winfo_ismapped():
    home_frame.pack_forget()
    config_frame.pack()

################# Menu #################
menu_btns_frame = Frame(root, width=SCREEN_WIDTH, height=MENU_HEIGHT, bg=MAIN_BG)
menu_btns_frame.pack(expand=True, fill=BOTH)

main_home_btn = Button(menu_btns_frame, text="Home", command=set_home_page)
main_config_btn = Button(menu_btns_frame, text="Config", command=set_config_page)

main_home_btn.pack(side=LEFT)
main_config_btn.pack(side=LEFT)
########################################  

# Main Views 
home_frame = Frame(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT-MENU_HEIGHT, bg=MAIN_BG)
home_frame.pack()

config_frame = Frame(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT-MENU_HEIGHT, bg=MAIN_BG)
############

############ Home Page ############

def take_screenshot():
  global ss_click_time
  if (time.perf_counter() - ss_click_time) > 2:
    ss_click_time = time.perf_counter()
    ss.take_test_screenshot()

def run_program():
  ss.main_loop()
  print("Running program")

take_screenshot_btn = Button(home_frame, text="Test Screenshot", command=take_screenshot)
take_screenshot_btn.place(relx=0.07, rely=0.1, width=120, height=40)

run_program_btn = Button(home_frame, text="Run!", command=run_program)
run_program_btn.place(relx=0.5, rely=0.2, anchor=CENTER, width=230, height=70)

output_text = StringVar()

output_label = Label(home_frame, textvariable=output_text, borderwidth=4, relief="ridge", bg="white")
output_label.place(rely=1+0.01 , relx=0.5, height=180, width=SCREEN_WIDTH+8, anchor=S)

###################################

############ Config Page ############
windows = ss.available_windows()
window_names = [x for x in windows.values()]
clicked_window = StringVar()
clicked_window.set(windows[str(ss.config["window_id"])])

path = StringVar()
path.set(ss.config["ss_path"])

step_validate = StringVar()
diff_perc_validate = StringVar()

save_file_success = StringVar()

def set_path():
  path_dir = filedialog.askdirectory()
  path.set(path_dir)

def save_config():
  global save_config_click_time
  if (time.perf_counter() - save_config_click_time) < 2:
    return
  save_config_click_time = time.perf_counter()
  print("saving")

  if validate_config():
    new_config = {
      "window_id": int(list(windows.keys())[list(windows.values()).index(clicked_window.get())]),
      "step": int(config_step_entry.get()),
      "ss_path": path.get(), 
      "diff_percentage": float(config_diff_perc_entry.get())
    }
  if ss.write_config_to_file(new_config):
    save_file_success.set("Saved!")
    ss.config = new_config
  else:
    save_file_success.set("Error!")

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

  return correct_values

config_window_id_label = Label(config_frame, text="Window ID").place(relx=0.05, rely=0.08)
config_window_id_op_menu = OptionMenu(config_frame, clicked_window, *window_names)
config_window_id_op_menu.place(relx=0.28, rely=0.08)

config_step_label = Label(config_frame, text="Step").place(relx=0.05, rely=0.08+0.08)
config_step_entry = Entry(config_frame)
config_step_entry.insert(0, ss.config["step"])
config_step_entry.place(relx=0.28, rely=0.08+0.08)
config_step_validate_label = Label(config_frame, textvariable=step_validate).place(relx=0.43, rely=0.08+0.08)

config_ss_path_label = Label(config_frame, text="Path").place(relx=0.05, rely=0.08+0.08+0.08)
config_ss_path_entry = Button(config_frame, text="Select Path!", command=set_path)
config_ss_path_entry.place(relx=0.28, rely=0.08+0.08+0.08)

config_ss_current_path_label = Label(config_frame, textvariable=path).place(relx=0.43, rely=0.08+0.08+0.08)

config_diff_perc_label = Label(config_frame, text="Percentage difference  [0.0; 100.0]").place(relx=0.05, rely=0.08+0.08+0.08+0.08)
config_diff_perc_entry = Entry(config_frame)
config_diff_perc_entry.insert(0, ss.config["diff_percentage"])
config_diff_perc_entry.place(relx=0.28, rely=0.08+0.08+0.08+0.08)
config_diff_perc_validate_label = Label(config_frame, textvariable=diff_perc_validate).place(relx=0.43, rely=0.08+0.08+0.08+0.08)

config_save = Button(config_frame, text="Save", command=save_config)
config_save.place(relx=0.28, rely=0.08+0.08+0.08+0.08+0.08+0.08)

save_file_success_info = Label(config_frame, textvariable=save_file_success).place(relx=0.28, rely=0.08+0.08+0.08+0.08+0.08+0.08+0.08)

###################################

root.mainloop()