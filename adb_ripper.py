import re
import cmd
import shlex
import shutil
import random
import argparse
import subprocess
from os import remove
from time import sleep
from pathlib import Path
from printit import Color as cl
from printit import PrintIt as pt
from maintent_utils import Maintenance as mt
from concurrent.futures import ThreadPoolExecutor as tpe

class AdbRipper(cmd.Cmd):

	prompt = f"{cl.WHITE_LINE}adbr{cl.RESET}> "
	
	def __init__(self, no_intro=False):
		super().__init__()
		self.no_intro = no_intro
		self.device = mt.check_device()
		if self.no_intro:
			self.intro = ""
		else:
			self.intro = pt.banner()
		
	def do_key(self, key):
		'''Send a key event to the target(NEED TO BE INTEGER).
		usage: key <INT>
		Ex: key 26
		'''
		cmd = shlex.split(key)
		cmd_l = len(cmd)
		if key and len(cmd) == 1:
			if mt.check_int(key):
				c, st, sd = mt.exec_cmd(["adb", "shell", "input", "keyevent", key])
				if c == 0:
					pt.success(f"Key event {cl.GREEN}{key}{cl.RESET} was sent.")
				else:
					pt.fail(f"Key event {cl.RED}{key}{cl.RESET} wasnt sent.")
			else:
				print("Please provide a valid key code.")
			return
		
		print(f"Incorrect usage, use {cl.RED}help key{cl.RESET}.")
			
	def do_multikey(self, keys):
		'''Send more than 1 key event to the target(NEED TO BE INTEGER).
		usage: key <INT>
		Ex: key 26 56 64 84
		'''
		items = shlex.split(keys)
		cmd_l = len(items)
		
		if len(items) >= 1:
			for key in items:
				if mt.check_int(key):
					c, st, sd = mt.exec_cmd(["adb","shell","input","keyevent",key])
					if c == 0:
						pt.success(f"Key event {cl.GREEN}{key}{cl.RESET} was sent.")
					else:
						pt.fail(f"Key event {cl.RED}{key}{cl.RESET} wasnt sent.")
				else:
					pt.fail(f"Invalid key event number: {cl.RED}{key}{cl.RESET}")
			return
				
		print(f"Incorrect usage, use {cl.RED}help multikey{cl.RESET}.")
				
	def do_search(self, args):
		'''Search files in the target device.
		usage: search <OPTIONS> <PATH>
		options: 
		 file - Search a file name in the path.
		 ex - Search a file by extension in the path.
		Ex: search ex .apk /
		 search ex .zip /sdcard/
		 search file app /sdcard/
		'''
		cmd = shlex.split(args)
		cmd_l = len(cmd)
		
		if len(cmd) == 3:
			
			if cmd[0] == "ex":
				if mt.check_regex(r"\.[a-z]{3,4}$", cmd[1]) and cmd[2].startswith("/sdcard"):
					c, st, sd = mt.exec_cmd(["adb", "shell", "find", cmd[2]])
					if c == 0:
						f = [item for item in sd.splitlines() if item.endswith(cmd[1])]
						pt.success("")
						for i in f:
							print(i)
					else:
						pt.fail(st)
			elif cmd[0] == "file":
				if cmd[2].startswith("/sdcard"):
					c2, st2, sd2 = mt.exec_cmd(["adb", "shell", "find", cmd[2]])
					if c2 == 0:
						f = [item for item in sd2.splitlines() if cmd[1] in item]
						pt.success("")
						print(f)
					else:
						pt.fail(st2)
			return
		
		print(f"Incorrect usage, use {cl.RED}help search{cl.RESET}.")
		
	def do_ripper(self, args):
		'''ADB Payload executor.
		usage: ripper <OPTION> 
		options: 
		 run, list
		Ex: 
		 ripper run payload_test 5(Delay for each execution.)
		 ripper list
		'''
		self.prompt = f"{cl.WHITE_LINE}adbr{cl.RESET}({cl.RED}ripper{cl.RESET})> "
		cmd = shlex.split(args)
		cmd_l = len(cmd)
		
		if len(cmd) == 3:
			
			if cmd[0] == "run" and mt.check_int(cmd[2]):
				
				
				if not cmd[1].endswith(".adbp"):
					cmd[1] += ".adbp"
					
				data = mt.f_reader(Path(f"adb_payloads/{cmd[1]}"))
				delay = max(1, int(cmd[2]))
									
				if len(data) == 2 and data[0] == None:
					pt.fail(data[1])
				else:	
					for line in data[0].splitlines():
						
						if mt.check_key(line):
							c, st, sd = mt.exec_cmd(["adb", "shell", "input", "keyevent", line])
							if c == 0:
								pt.success(f"Keyevent '{line}' was sent.")
							else:
								pt.fail(f"Keyevent '{line}' wasnt sent.")
								
						elif mt.check_text(line):
							if line == "## File created by adb_ripper":
								print("Comment passed.")
							else:
								c, st, sd = mt.exec_cmd(["adb", "shell", "input", "text", line.replace(' ', '_')])
								if c == 0:
									pt.success(f"Text '{line}' was sent.")
								else:
									pt.fail(f"Text '{line}' wasnt sent.")
									
						sleep(delay)
			return
		
		elif len(cmd) == 1:
			if cmd[0] == "list":
				if mt.check_path(Path("adb_payloads")):
					pt.success("")
					for p in Path("adb_payloads").glob("*.adbp"):
						print(p.name)
				else:
					print(f"The {cl.GREEN}adb_payloads{cl.RESET} dont exists.")
			return
					
		print(f"Unknown instructions, use {cl.RED}help ripper{cl.RESET}.")
							
	def do_edit(self, arg):
		'''Edit the content for any file that you choose.
		usage: edit <FILE_PATH>
		Ex: 
		 edit /home/admin/file.txt
		'''
		
		cmd = shlex.split(arg)
		cmd_l = len(cmd)
		
		if not arg:
			print("Please provide a valid file path.");return
			
		elif cmd_l == 1:
			try:
				p = Path(arg).resolve()
				if p.exists():
					subprocess.run(["nano", p])
				else:
					p.write_text("## File created by adb_ripper")
					subprocess.run(["nano", p])
			except Exception as e:
				pt.error(f"Error: {str(e)}")
			return
		
		print(f"Incorrect usage, use {cl.RED}help edit{cl.RESET}.")
		
	def do_del(self, arg):
		'''Deletes a file.
		usage: del <FILE_PATH>
		Ex:
		 del file.txt
		 del /home/admin/secret.dat
		'''
		
		cmd = shlex.split(arg)
		cmd_l = len(cmd)
		
		if not arg:
			print("Please provide a valid file path.");return
			
		elif cmd_l == 1:
			try:
				p = Path(arg).resolve()
				if p.exists() and p.is_file():
					remove(p)
				else:
					print("File doesnt exists.")
			except Exception as e:
				pt.error(str(e))
			return
				
		print(f"Incorrect usage, use {cl.RED}help del{cl.RESET}.")
	
	def do_clear_pkg(self, args):
		'''Clear a target package data.
		usage: clear_pkg <PACKAGE_NAME>
		Ex:
		 clear_pkg com.termux
		 clear_pkg com.whatsapp
		'''
		cmd = shlex.split(args)
		cmd_l = len(cmd)
		
		if not args:
			print("Please provide a package name.");return
		
		elif cmd_l == 1:
			package = cmd[0]
			if re.match(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$", package):
				c, st, sd = mt.exec_cmd(["adb", "shell", "pm", "clear", package])
				if c == 0:
					pt.success(f"Package data in '{package}' was wiped.")
				else:
					pt.fail(f"Package data in '{package}' couldnt be wiped.")
			else:
				print("Set a valid package name.")
			return
		
		print(f"Incorrect usage, use {cl.RED}help clear_pkg{cl.RESET}.")
		
	def do_uninstall(self, args):
		'''Uninstall a target package.
		usage: uninstall <PACKAGE_NAME>
		Ex:
		 uninstall com.termux
		 uninstall com.whatsapp
		 uninstall tv.cinema
		'''
		cmd = shlex.split(args)
		cmd_l = len(cmd)
		
		if not args:
			print("Please provide a package name.");return
		
		elif cmd_l == 1:
			package = cmd[0]
			
			if re.match(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$", package):
				c, st, sd = mt.exec_cmd(["adb", "uninstall", package])
				if c == 0:
					pt.success(f"Package '{package}' was removed.")
				else:
					pt.fail(f"Package '{package}' couldnt be removed: {st}")
			else:
				print(f"Invalid package, use {cl.RED}help uninstall{cl.RESET}.")
			
			return
				
		print(f"Unknown instructions, use {cl.RED}help uninstall{cl.RESET}.")
		
	def do_install(self, args):
		'''Install a target package from storage.
		usage: install <LOCAL_APK_PATH>
		Ex:
		 install /home/admin/app.apk
		 install app.apk
		'''
		cmd = shlex.split(args)
		cmd_l = len(cmd)

		if not args:
			print("Please provide a package name.");return

		elif cmd_l == 1:
			apk = cmd[0]
			if apk.endswith(".apk"):
				pt.proc(f"Trying to install '{apk}' in target device.")
				c, st, sd = mt.exec_cmd(["adb", "install", apk])
				if c == 0:
					pt.success(f"Package '{apk}' was installed.")
				else:
					pt.fail(f"Package '{apk}' couldnt be installed: {st}")
			return

		print(f"Unknown instructions, use {cl.RED}help install{cl.RESET}.")
		
	def do_sysinf(self, args):
		'''Shows device informations.'''
		
		sys_dict = mt.sysinf()
		
		if sys_dict:
			print("")
			for i, v in sys_dict.items():
				print(f"{cl.GREEN}{i}{cl.RESET}: {v}")
		else:
			pt.fail("System informations are not accessible.")
				
	def do_getpro(self, args):
		'''Get device properties.'''
		
		c, st, sd = mt.exec_cmd(["adb", "shell", "getprop"])
		
		if c == 0:
			pt.success("")
			print(sd)
		else:
			pt.fail(st)
	
	def do_shell(self, args):
		'''Open a raw shell in the target.'''
		subprocess.run(["adb","shell"])		
			
	def do_send(self, args):
		'''Send an file to the target.
		usage: send <LOCAL_PATH> <TARGET_PATH>
		Ex:
		 send file.dat /sdcard/
		 send /home/admin/app.apk /sdcard/Download/
		'''
		
		cmd = shlex.split(args)
		cmd_l = len(cmd)
		
		if cmd_l == 2:
			
			try:
				paths = [Path(cmd[0]), Path(cmd[1])]
				c, st, sd = mt.exec_cmd(["adb", "push", cmd[0], cmd[1]])
				if c == 0:
					pt.success(f"File '{cmd[0]}' was sent to the target.")
				else:
					pt.fail(f"File '{cmd[0]}' couldnt be send the target.")
			except Exception as e:
				pt.error(str(e));return
			
			return
		
		print(f"Incorrect usage, use {cl.RED}help send{cl.RESET}.")
				
	def do_logcat(self, args):
		'''Displays target device logcat.'''
		subprocess.run(["adb", "logcat", "-L"])
		
	def do_list_pkgs(self, args):
		'''List all device packages.
		usage: list <OPTIONS>
		Ex:
		 list
		 list search termux
		'''
		cmd = shlex.split(args)
		cmd_l = len(cmd)
		
		if cmd_l == 0:
			c, st, sd = mt.exec_cmd(["adb", "shell", "pm", "list" ,"packages"])
			if c == 0:
				pt.success("")
				lines = [line.split(":")[1] for line in sd.splitlines()]
				for line in lines:
					print(line)
					sleep(0.005)
			else:
				pt.fail(f"Cant list packages: {st}")
			return
		
		elif cmd_l == 2 and cmd[0] == "search":
			c, st, sd = mt.exec_cmd(["adb", "shell", "pm", "list" ,"packages"])
			if c == 0:
				pt.success("")
				lines = [line.split(":")[1] for line in sd.splitlines()]
				for l in lines:
					if cmd[1] in l:
						print(l)
			return
		
		print(f"Unknown instructions, use {cl.RED}help list_pkgs{cl.RESET}.")
		
	def do_start_app(self, package_name):
		'''Starts a application on target by package name.
		usage: start_app <PACKAGE_NAME>
		Ex:
		 start_app com.termux
		 start_app com.whatsapp
		'''
		
		cmd = shlex.split(package_name)
		cmd_l = len(cmd)
		
		if cmd_l == 1:
			c, st, sd = mt.exec_cmd(
				["adb", "shell", "cmd", "package", "resolve-activity", "--brief", cmd[0]]
			)
			if c == 0:
				final_str = sd.splitlines()[-1]
				c1, st1, sd1 = mt.exec_cmd(["adb", "shell", "am", "start", "-n", final_str])
				if c1 == 0:
					pt.success(f"App '{cmd[0]}' started.")
				else:
					pt.fail(f"App '{cmd[0]}' couldnt be started: {st1}")
			else:
				pt.fail("The program couldnt get package >MAIN<.")
			return
		
		print(f"Incorrect usage, use {cl.RED}help start_app{cl.RESET}.")
		
		
	def do_dump(self, args):
		'''Dump a target device file to your device.
		usage: dump <TARGET_PATH> <LOCAL_PATH>
		Ex:
		 send /sdcard/file.dat /home/admin/
		 send /sdcard/Download/app.apk /home/admin/
		'''
		
		cmd = shlex.split(args)
		cmd_l = len(cmd)
		
		if cmd_l == 2:
			
			c, st, sd = mt.exec_cmd(["adb", "pull", cmd[0], cmd[1]])
			if c == 0:
				pt.success(f"File '{cmd[0]}' was dumped to '{cmd[1]}'.")
			else:
				pt.fail(f"File '{cmd[0]}' cant be dumped.")
			return

		print(f"Incorrect usage, use {cl.RED}help dump{cl.RESET}.")
				
	def do_dump_sd(self, args):
		'''Dump what kind of data you want in '/sdcard/'.
		usage: dump_sd <EXTENSION>
		Ex:
		 dump_sd html - Dump html pages
		 dump_sd txt - Dump text files
		 dump_sd png,jpg,jpeg,heic - Dump photos
		 dump_sd doc,docx,pdf,xlsx - Dump documents
		 dump_sd png,pdf - Only .png photos and .pdf files.
		'''
		
		def process_file(item):
			try:
				p = Path(item).suffix
				_type = mt.get_file_type(p)
				full_path = f"adb_dumps/{self.device}/{_type}/"
				Path(full_path).mkdir(parents=True, exist_ok=True)
				pt.proc(f"Dumping '{item}'.")
				c1, st1, sd1 = mt.exec_cmd(["adb", "pull", item, full_path])
				if c1 == 0:
					pt.success(f"File '{item}' was dumped to '{full_path}'.")
				else:
					pt.error(f"Failed to dump '{item}': {st1}.")
			except KeyboardInterrupt:
				pt.error(f"Dumping process ended, visit 'adb_dumps/{self.device}' to find your dumps.")
			except Exception as e:
				pt.error(f"Error: {e}.")
				
		def _list_this_shit(search_exts: tuple):
			
			c, st, sd = mt.exec_cmd(["adb","shell","find","/sdcard/", "-type", "f"])
			
			if c != 0 or not sd:
				pt.fail("Failed to find files.")
				return
			
			with tpe(max_workers=4) as exe:
				exe.map(
					process_file,
					(line for line in sd.split("\n") if line.lower().endswith(search_exts))
				)
		
		Path(f"adb_dumps/{self.device}").mkdir(parents=True, exist_ok=True)
		
		if not args:
			print(f"Please provide args, or use {cl.RED}help dump_sd{cl.RESET}."); return
		
		cmd = shlex.split(args)
		cmd_l = len(cmd)
		
		if "," in cmd[0] and cmd_l == 1:
			
			exts = tuple(
				ext if ext.startswith(".") else f".{ext}" 
				for item in cmd[0].split(",")
				if re.match(r"^\.?[a-z]{3,5}$", (ext := item.strip().lower()))
			)
			
			_list_this_shit(exts)
				
			return
		
		elif "," not in args and cmd_l == 1:	
			
			if not cmd[0].startswith("."):
				cmd[0] = "."+cmd[0]
				
			_list_this_shit((cmd[0],))
			
			return
		
		print(f"Incorrect usage, use {cl.RED}help dump_sd{cl.RESET}.")
				
	def do_dump_wpp(self, args):
	    '''Try dump high priority whatsapp data.'''
	
	    BASE_REMOTE = "/sdcard/Android/media/com.whatsapp/WhatsApp/Media"
	
	    def list_files(remote_path):
	        c, st, sd = mt.exec_cmd([
	            "adb", "shell", "find", remote_path, "-type", "f"
	        ])
	        if c != 0 or not sd:
	            pt.fail(f"Failed to list files in '{remote_path}'")
	            return []
	        return sd.splitlines()
	
	    def pull_file(remote_file):
	        try:
	            pt.proc(f"Pulling '{remote_file}'")
	
	            c, st, sd = mt.exec_cmd([
	                "adb", "pull", remote_file, str(base_p)
	            ])
	
	            if c == 0:
	                pt.success(f"Pulled '{remote_file}'")
	            else:
	                pt.fail(f"Failed '{remote_file}': {st}")
	
	        except Exception as e:
	            pt.error(str(e))
	
	    def format_files(src_path):
	        _format = mt.get_file_type(src_path.suffix)
	        dest = base_p / f"{_format}"
	        dest.mkdir(parents=True, exist_ok=True)
	
	        dest_file = dest / src_path.name
	
	        try:
	            if dest_file.exists():
	                if mt.file_hash(src_path) == mt.file_hash(dest_file):
	                    return
	                else:
	                    counter = 1
	                    new_dest = dest_file
	                    while new_dest.exists():
	                        new_dest = dest / f"{src_path.stem}_{counter}{src_path.suffix}"
	                        counter += 1
	                    shutil.move(str(src_path), str(new_dest))
	            else:
	                shutil.move(str(src_path), str(dest_file))
	        except Exception as e:
	            pt.fail(str(e))
	
	    if mt.check_wpp_path():
	        base_p = Path(f"adb_dumps/{self.device}/WhatsApp")
	        base_p.mkdir(parents=True, exist_ok=True)
	
	        wpp_dirs = [
	            "WhatsApp Audio",
	            "WhatsApp Documents",
	            "WhatsApp Images",
	            "WhatsApp Profile Photos",
	            "WhatsApp Video",
	            "WhatsApp Video Notes",
	            "WhatsApp Voice Notes",
	        ]
	
	        all_files = []
	
	        for path in wpp_dirs:
	            remote = f"{BASE_REMOTE}/{path}"
	            pt.proc(f"Scanning '{remote}'")
	            files = list_files(remote)
	            all_files.extend(files)
	
	        if not all_files:
	            pt.fail("No files found.")
	            return
	
	        with tpe(max_workers=3) as exe:
	            exe.map(pull_file, all_files)
	
	        files = [p for p in base_p.rglob("*") if p.is_file()]
	        with tpe(max_workers=6) as exe:
	            exe.map(format_files, files)

	        for w_path in wpp_dirs:
	            wpp_path = base_p / w_path
	            if wpp_path.exists():
	                shutil.rmtree(wpp_path)
	
	    else:
	        pt.fail("Cant access whatsapp folder.")
	
		
							
	def do_check_connection(self, args):
		'''Check if theres a device connected.'''
		try:
			check = mt.check_device()
			if check:
				pt.success(f"The connected device is '{check}'")
			else:
				pt.fail(f"No device conected.")
		except Exception as e:
			pt.error(str(e))
			
	def do_screenrecord(self, args):
		'''Records screen of the target device.
		usage: screenrecord 
		'''
		if not args:
			filename = f"REC_{mt.get_time()}.mp4"
			try:				
				pt.success("Screen recording started, press CTRL + C to stop.")
				try:
					subprocess.run(["adb", "shell", "screenrecord", f"/sdcard/{filename}"])
				except KeyboardInterrupt:
					sleep(3)
					c, st, sd = mt.exec_cmd(["adb", "pull", f"/sdcard/{filename}", f"adb_dumps/{self.device}"])
					if c == 0:
						pt.success(f"File '{filename}' was saved on adb_dumps/{self.device}.")
						q = pt.question("Do you want to open this recording?(y/n): ")
						if q.lower() == "y":
							mt.open_file(f"adb_dumps/{self.device}/{filename}")
						else:
							return
			except Exception as e:
				print(str(e))
			return
			
		print(f"Incorrect usage, use {cl.RED}help screenrecord{cl.RESET}.")
			
	def do_screencap(self, args):
		'''Take a screenshot of the target device.
		usage: screencap
		'''
		if not args:
			filename = f"SCREENSHOT_{mt.get_time()}.png"
			try:				
				c, st, sd = mt.exec_cmd(["adb", "shell", "screencap", f"/sdcard/{filename}"])
				if c == 0:
					c1, st1, sd1 = mt.exec_cmd(["adb", "pull", f"/sdcard/{filename}", f"adb_dumps/{self.device}"])
					if c1 == 0:
						pt.success(f"File '{filename}' was saved on adb_dumps/{self.device}.")
						q = pt.question("Do you want to open this screenshot?(y/n): ")
						if q.lower() == "y":
							mt.open_file(f"adb_dumps/{self.device}/{filename}")
						else:
							return
			except Exception as e:
				print(str(e))
			return
		
		print(f"Incorrect usage, use {cl.RED}help screenrecord{cl.RESET}.")
		
	def do_ls(self, args):
		'''Lists folders and content.
		usage: ls <PATH>
		Ex:
		 ls
		 ls /
		'''
		
		cmd = shlex.split(args)
		cmd_l = len(cmd)
		
		if cmd_l == 0:
			p = Path.cwd()
			p_data = mt.path_runner(p)
			if p_data:
				pt.success(f"Content of '{p}':")
				for p in p_data:
					print(p)
					sleep(0.01)
			else:
				pt.fail(f"Failed to list path content: {p_data}")
			return
		
		elif cmd_l == 1 and "-" not in cmd[0][0]:
			p = Path(cmd[0])
			p_data = mt.path_runner(p)
			if p_data:
				pt.success(f"Content of '{p}':")
				for p in p_data:
					print(p)
					sleep(0.01)
			else:
				pt.fail(f"Failed to list path content: {p_data}")
			return
		
		print(f"Incorrect usage, use {cl.RED}help ls{cl.RESET}.")
		
	def do_cat(self, args):
		'''Shows files content
		usage: cat <FILE_PATH>
		Ex:
		 cat /etc/os-release
		'''
		
		cmd = shlex.split(args)
		cmd_l = len(cmd)
		
		if cmd_l == 1:
			file_path = Path(cmd[0])
			try:
				c, d = mt.read_c(file_path)
				if c == 0:
					pt.success(f"'{file_path}':")
					print(d)
				else:
					pt.fail(f"Error while reading content: {d}")
			except TypeError:
				pt.fail(f"The file '{file_path}' dont exists.")
			return
		
		print(f"Incorrect usage, use {cl.RED}help dump{cl.RESET}.")
		
			
	def do_wipe(self, args):
		'''Wipe any file on target device.
		usage: wipe <TARGET_PATH>
		Ex:
		 wipe /sdcard/file.mp4
		'''
		
		cmd = shlex.split(args)
		cmd_l = len(cmd)
		
		if cmd_l == 1 and "/sdcard/" in cmd[0]:
			if mt.check_rm_sh():
				c, st, sd = mt.exec_cmd(["adb", "shell", "sh", f"/sdcard/rm.sh", cmd[0]])
				if c == 0:
					pt.success(f"File '{cmd[0]}' deleted from device storage.")
				else:
					pt.fail(f"File '{cmd[0]}' cant be deleted: {st}")
			else:
				c1, st1, sd1 = mt.exec_cmd(
					["adb", "push", "rm.sh", "/sdcard/"]
				)
				if c1 == 0 and mt.check_rm_sh():
					c2, st2, sd2 = mt.exec_cmd(["adb", "shell", "sh", "/sdcard/rm.sh", cmd[0]])
					if c2 == 0:
						pt.success(f"File '{cmd[0]}' deleted from device storage.")
					else:
						pt.fail(f"File '{cmd[0]}' cant be deleted: {st2}.")
				else:
					pt.fail("Couldnt send script 'rm.sh' to '/sdcard/'.")
			return
		
		print(f"Unknown instructions, use {cl.RED}help wipe{cl.RESET}.")
			
	def do_banner(self, arg):
		'''Displays a banner on the screen.'''
		pt.banner()
		
	def do_back(self, arg):
		'''Back to default terminal.'''	
		self.prompt = f"{cl.WHITE_LINE}adbr{cl.RESET}> "
	
	def do_exit(self, arg):
		return True
		
	def do_clear(self, arg):
		'Clear the console display.'
		mt.clear()
		
parser = argparse.ArgumentParser(
	description="ADB Ripper, A useful program focused in exploit adb functions."
)
parser.add_argument("-i", action="store_true", help="Activate interactive connection.")
parser.add_argument("-q", action="store_true", help="Run without banner")
args = parser.parse_args()

def run(i: bool, q: bool):
	d = mt.check_device()
	
	if i and not d:
		c = mt.connect_device()
		if not c:
			print("Can't connect to device.")
		d = mt.check_device()
	
	if d:
		mt.check_paths(d)
		AdbRipper(no_intro=q).cmdloop()
	else:
		print("No device connected.")
			
if __name__ == "__main__":
	if mt.check_adb():
		run(args.i, args.q)
	else:
		print("Please install android-tools.")
		
