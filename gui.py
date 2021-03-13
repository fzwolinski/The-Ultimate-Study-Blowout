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
  ss.take_test_screenshot()

def run_program():
  # TODO
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

config_window_id_label = Label(config_frame, text="Window ID").place(relx=0.05, rely=0.08)
config_window_id_entry = Entry(config_frame)
config_window_id_entry.insert(0, ss.config["window_id"])
config_window_id_entry.place(relx=0.25, rely=0.08)

config_step_label = Label(config_frame, text="Step").place(relx=0.05, rely=0.08+0.08)
config_step_entry = Entry(config_frame)
config_step_entry.insert(0, ss.config["step"])
config_step_entry.place(relx=0.25, rely=0.08+0.08)

config_ss_path_label = Label(config_frame, text="Path").place(relx=0.05, rely=0.08+0.08+0.08)
config_ss_path_entry = Entry(config_frame)
config_ss_path_entry.insert(0, ss.config["ss_path"])
config_ss_path_entry.place(relx=0.25, rely=0.08+0.08+0.08)

config_diff_perc_label = Label(config_frame, text="Percentage difference").place(relx=0.05, rely=0.08+0.08+0.08+0.08)
config_diff_perc_entry = Entry(config_frame)
config_diff_perc_entry.insert(0, ss.config["diff_percentage"])
config_diff_perc_entry.place(relx=0.25, rely=0.08+0.08+0.08+0.08)

###################################


root.mainloop()



"""
- Start programu

- Flagi: -w -t...

Config:
  - Inputy z wartosciami configu
  - Save config button 




"""