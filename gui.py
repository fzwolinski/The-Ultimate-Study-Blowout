from tkinter import *
import time

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600 

MENU_HEIGHT = 26

MAIN_BG = "#fff1e5"

root = Tk()
root.title("SmartStudent")
root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}") 
root.resizable(False,False)

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

################# Home Page ############

def take_screenshot():
  # TODO
  print("Taking screenshot")

def run_program():
  # TODO
  print("Running program")

take_screenshot_btn = Button(home_frame, text="Test Screenshot", command=take_screenshot)
take_screenshot_btn.place(relx=0.07, rely=0.1, width=120, height=40)

run_program_btn = Button(home_frame, text="Run!", command=run_program)
run_program_btn.place(relx=0.5, rely=0.2, anchor=CENTER, width=230, height=70)

output_text = StringVar()
output_text.set("Output Here")
output_label = Label(home_frame, textvariable=output_text, borderwidth=4, relief="ridge", bg="white")
output_label.place(rely=1+0.01 , relx=0.5, height=180, width=SCREEN_WIDTH+8, anchor=S)

########################################



root.mainloop()



"""
- Start programu

- Flagi: -w -t...

Config:
  - Inputy z wartosciami configu
  - Save config button 




"""