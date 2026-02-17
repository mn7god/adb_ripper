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
		if len(banner.splitlines()) >= 2:
			for line in banner.splitlines():
				print(color+line+Color.RESET)
				sleep(0.1)
		else:
			for i in range(len(banner)):
				print(color+banner[i], end="", flush=True)
				sleep(random.uniform(0.01, 0.07))
			print(Color.RESET)
		print(f"use {Color.RED}help{Color.RESET} to display available commands.")
	def success(msg):
		print(f"[{Color.GREEN}SUCCESS{Color.RESET}]: {msg}")
	def fail(msg):
		print(f"[{Color.RED}FAIL{Color.RESET}]: {msg}")
	def error(msg):
		print(f"[{Color.YELLOW}ERROR{Color.RESET}]: {msg}")
	def proc(msg):
		print(f"[{Color.YELLOW}PROCESS{Color.RESET}]: {msg}")
	def info(msg):
		print(f"[{Color.WHITE}INFO{Color.RESET}]: {msg}")
	def question(msg):
		i = input(f"[{Color.GRAY}QUESTION{Color.RESET}]: {msg}")
		return i
		
