import random
from os import system
from time import sleep

class Color:
    RED = "\033[91m"        
    GREEN = "\033[1;49;92m"   
    DARK_GREEN = "\033[2;49;32m" 
    WHITE = "\033[97m"      
    WHITE_4 = "\033[1;49;39m"
    YELLOW = "\033[93m"
    BLUE = "\033[0;94m"     
    PURPLE = "\033[0;95m"   
    CYAN = "\033[0;96m"
    NEGATIVE = "\033[7m"
    RESET = "\033[0m"
    GRAY = "\033[2;49;37m"
    GRAY_2 = "\033[2;49;39m"
    WHITE_LINE = "\033[4;49;97m"
    DARK_GREEN_LINE = "\033[4;49;32m"

class PrintIt:
    def banner():
        system("clear")
        colors = [Color.RED, Color.GREEN, Color.WHITE, Color.NEGATIVE]
        banner = ''' ▄▄▄      ▓█████▄  ▄▄▄▄       ██▀███   ██▓ ██▓███   ██▓███  ▓█████  ██▀███  
▒████▄    ▒██▀ ██▌▓█████▄    ▓██ ▒ ██▒▓██▒▓██░  ██▒▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒
▒██  ▀█▄  ░██   █▌▒██▒ ▄██   ▓██ ░▄█ ▒▒██▒▓██░ ██▓▒▓██░ ██▓▒▒███   ▓██ ░▄█ ▒
░██▄▄▄▄██ ░▓█▄   ▌▒██░█▀     ▒██▀▀█▄  ░██░▒██▄█▓▒ ▒▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄  
 ▓█   ▓██▒░▒████▓ ░▓█  ▀█▓   ░██▓ ▒██▒░██░▒██▒ ░  ░▒██▒ ░  ░░▒████▒░██▓ ▒██▒
 ▒▒   ▓▒█░ ▒▒▓  ▒ ░▒▓███▀▒   ░ ▒▓ ░▒▓░░▓  ▒▓▒░ ░  ░▒▓▒░ ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░
  ▒   ▒▒ ░ ░ ▒  ▒ ▒░▒   ░      ░▒ ░ ▒░ ▒ ░░▒ ░     ░▒ ░      ░ ░  ░  ░▒ ░ ▒░
  ░   ▒    ░ ░  ░  ░    ░      ░░   ░  ▒ ░░░       ░░          ░     ░░   ░ 
      ░  ░   ░     ░            ░      ░                       ░  ░   ░     
           ░            ░'''
        color = random.choice(colors)
        print(color+banner+Color.RESET)
        sleep(0.1)
        print(f"use {Color.RED}help{Color.RESET} to display available commands.")
        
    def success(msg):
        print(f"[{Color.GREEN}SUCCESS{Color.RESET}]: {msg}")
        
    def fail(msg):
        print(f"[{Color.RED}FAIL{Color.RESET}]: {msg}")
        
    def error(msg):
        print(f"[{Color.RED}ERROR{Color.RESET}]: {msg}")
        
    def proc(msg):
        print(f"[{Color.YELLOW}PROCESS{Color.RESET}]: {msg}")
        
    def info(msg):
        print(f"[{Color.WHITE}INFO{Color.RESET}]: {msg}")
        
    def question(msg):
        i = input(f"[{Color.GRAY}QUESTION{Color.RESET}]: {msg}")
        return i
        
    def yes_no(msg):
        i = input(f"[{Color.GRAY}QUESTION{Color.RESET}]: {msg}(yes/no): ")
        return i.lower().strip() in ("yes", "yy", "y")

    def incorrect_usage(cmd):
        print(f"[{Color.RED}ERROR{Color.RESET}]: Incorrect usage of '{cmd}', use 'help {cmd}'")
        
        
        
        
