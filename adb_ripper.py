import cmd
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

class AdbRipper(cmd.Cmd):
	
	device = mt.check_device()
	intro = pt.banner()
	prompt = f"{cl.WHITE_LINE}adbr{cl.RESET}> "
	
	def do_key(self, key):
		'''Send a key event to the target(NEED TO BE INTEGER).
		usage: key <INT>
		Ex: key 26
		'''
		cmd = key.split()
		cmd_l = len(cmd)
		if key and len(cmd) == 1:
			if mt.check_int(key):
				c, st, sd = mt.exec_cmd(f"adb shell input keyevent {key}")
				if c == 0:
					pt.success(f"Key event {cl.GREEN}{key}{cl.RESET} was sent.")
				else:
					pt.fail(f"Key event {cl.RED}{key}{cl.RESET} wasnt sent.")
			else:
				print("Please provide a valid key code.")
		elif cmd_l < 1:
			print(f"Too few args, use {cl.RED}help key{cl.RESET}.")
		elif cmd_l > 1:
			print(f"Too many args, use {cl.RED}help key{cl.RESET}.")
			
	def do_multikey(self, keys):
		'''Send more than 1 key event to the target(NEED TO BE INTEGER).
		usage: key <INT>
		Ex: key 26 56 64 84
		'''
		items = keys.split(" ")
		cmd_l = len(items)
		if len(items) >= 1:
			for key in items:
				if key and mt.check_int(key):
					c, st, sd = mt.exec_cmd(f"adb shell input keyevent {key}")
					if c == 0:
						pt.success(f"Key event {cl.GREEN}{key}{cl.RESET} was sent.")
					else:
						pt.fail(f"Key event {cl.RED}{key}{cl.RESET} wasnt sent.")
				else:
					print("Please provide a valid key code.")
		else:
			print(f"Too few args, use {cl.RED}help multikey{cl.RESET}.")
				
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
		cmd = args.split(" ")
		cmd_l = len(cmd)
		if len(cmd) == 3:
			if cmd[0] == "ex":
				if cmd[1][0] == "." and cmd[2][0] == "/":
					c, st, sd = mt.exec_cmd(f"adb shell find {cmd[2]} | grep {cmd[1]}", use_sh=True)
					if c == 0:
						pt.success("")
						print(sd)
					else:
						pt.fail(st)
			elif cmd[0] == "file":
				if cmd[2][0] == "/":
					c2, st2, sd2(f"adb shell find {cmd[2]} | grep {cmd[1]}", use_sh=True)
					if c2 == 0:
						pt.success("")
						print(sd2)
					else:
						pt.fail(st2)
		elif cmd_l < 3:
			print(f"Too few args, use {cl.RED}help search{cl.RESET}.")
		elif cmd_l > 3:
			print(f"Too many args, use {cl.RED}help search{cl.RESET}.")
		return
		
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
		cmd = args.split()
		cmd_l = len(cmd)
		if len(cmd) == 3:
			if cmd[0] == "run" and mt.check_int(cmd[2]):
				if ".adbp" in cmd[1]:
					data = mt.f_reader(Path(f"adb_payloads/{cmd[1]}"))
					if len(data) == 2 and data[0] == None:
						pt.fail(data[1])
					else:
						for item in data[0].splitlines():
							if mt.check_key(item):
								c, st, sd = mt.exec_cmd(f"adb shell input keyevent {item}")
								if c == 0:
									pt.success(f"Keyevent {item} was sent.")
								else:
									pt.fail(f"Keyevent {item} wasnt sent.")
							elif mt.check_text(item):
								if item == "## File created by adb_ripper":
									print("Comment passed.")
								else:
									c, st, sd = mt.exec_cmd(f"adb shell input text {item.replace(" ", "_")}")
									if c == 0:
										pt.success(f"Text '{item}' was sent.")
									else:
										pt.fail(f"Text '{item}' wasnt sent.")
							sleep(int(cmd[2]))
				elif "." not in cmd[1]:
					data = mt.f_reader(Path(f"adb_payloads/{cmd[1]}.adbp"))
					if len(data) == 2 and data[0] == None:
						pt.fail(data[1])
					else:
						for item in data[0].splitlines():
							if mt.check_key(item):
								c, st, sd = mt.exec_cmd(f"adb shell input keyevent {item}")
								if c == 0:
									pt.success(f"Keyevent {item} was sent.")
								else:
									pt.fail(f"Keyevent {item} wasnt sent.")
							elif mt.check_text(item):
								if item == "## File created by adb_ripper":
									print("Comment passed.")
								else:
									c, st, sd = mt.exec_cmd(f"adb shell input text {item.replace(" ", "_")}")
									if c == 0:
										pt.success(f"Text '{item}' was sent.")
									else:
										pt.fail(f"Text '{item}' wasnt sent.")
							sleep(int(cmd[2]))
				else:
					print("Invalid file type.")
		
		elif len(cmd) == 1:
			if cmd[0] == "list":
				if mt.check_path(Path("adb_payloads")):
					pt.success("")
					for p in Path("adb_payloads").rglob("*.adbp"):
						print(p.name)
				else:
					print(f"The {cl.GREEN}adb_payloads{cl.RESET} dont exists.")
					
		elif cmd_l < 1:
			print(f"Too few args, use {cl.RED}help ripper{cl.RESET}.")
			
		else:
			print(f"Unknown instructions, use {cl.RED}help ripper{cl.RESET}.")
			
					
		return
							
	def do_edit(self, arg):
		'''Edit the content for any file that you choose.
		usage: edit <FILE_PATH>
		Ex: 
		 edit /home/admin/file.txt
		'''
		cmd = arg.split()
		cmd_l = len(cmd)
		if not arg:
			print("Please provide a valid file path.")
		elif cmd_l == 1:
			try:
				p = Path(arg).resolve()
				if p.exists():
					subprocess.run(f"nano {p}", shell=True, text=True)
				else:
					p.write_text("## File created by adb_ripper")
					subprocess.run(f"nano {p}", shell=True, text=True)
			except Exception as e:
				pt.error({str(e)})
		elif cmd_l > 1:
			print(f"Too many args, use {cl.RED}help edit{cl.RESET}.")
		return
		
	def do_del(self, arg):
		'''Deletes a file.
		usage: del <FILE_PATH>
		Ex:
		 del file.txt
		 del /home/admin/secret.dat
		'''
		b_size = 4 * 1024
		cmd = arg.split()
		cmd_l = len(cmd)
		if not arg:
			print("Please provide a valid file path.")
		elif cmd_l == 1:
			try:
				p = Path(arg).resolve()
				if p.exists() and p.is_file():
					with p.open("r+b") as f:
						while chunk := f.read(b_size):
							chunk_len = len(chunk)
							f.seek(-chunk_len, 1)
							f.write(bytes(random.getrandbits(8) for _ in range(chunk_len)))
					remove(p)
				else:
					print("File doesnt exists.")
			except Exception as e:
				pt.error(str(e))
		elif cmd_l > 1:
			print(f"Too many args, use {cl.RED}help del{cl.RESET}.")
		return
	
	def do_clear_pkg(self, args):
		'''Clear a target package data.
		usage: clear_pkg <PACKAGE_NAME>
		Ex:
		 clear_pkg com.termux
		 clear_pkg com.whatsapp
		'''
		cmd = args.split()
		cmd_l = len(cmd)
		if not args:
			print("Please provide a package name.")
		elif cmd_l == 1:
			allowed_names = [
				"com", 
				"org", 
				"tv", 
				"app", 
				"android", 
				"ai", 
				"vendor", 
			]
			condition = True if "." in cmd[0] and cmd[0].split(".")[0] in allowed_names else False
			if condition:
				c, st, sd = mt.exec_cmd(f"adb shell pm clear {cmd[0]}")
				if c == 0:
					pt.success(f"Package data in '{cmd[0]}' was wiped.")
				else:
					pt.fail(f"Package data in '{cmd[0]}' couldnt be wiped.")
			else:
				print("Set a valid package name.")
		elif cmd_l > 1:
			print(f"Too many args, use {cl.RED}help clear_pkg{cl.RESET}.")
		return
		
	def do_uninstall(self, args):
		'''Uninstall a target package.
		usage: uninstall <PACKAGE_NAME>
		Ex:
		 uninstall com.termux
		 uninstall com.whatsapp
		 uninstall tv.cinema
		'''
		cmd = args.split()
		cmd_l = len(cmd)
		if not args:
			print("Please provide a package name.")
		elif cmd_l == 1:
			allowed_names = [
				"com", 
				"org", 
				"tv", 
				"app", 
				"android", 
				"ai", 
				"vendor", 
			]
			condition = True if "." in cmd[0] and cmd[0].split(".")[0] in allowed_names else False
			if condition:
				c, st, sd = mt.exec_cmd(f"adb uninstall {cmd[0]}")
				if c == 0:
					pt.success(f"Package '{cmd[0]}' was removed.")
				else:
					pt.fail(f"Package '{cmd[0]}' couldnt be removed: {st}")
			else:
				print(f"Invalid package, use {cl.RED}help uninstall{cl.RESET}.")
		elif cmd_l > 1:
			print(f"Too few args, use {cl.RED}help uninstall{cl.RESET}.")
		else:
			print(f"Unknown instructions, use {cl.RED}help uninstall{cl.RESET}.")
		return
		
	def do_install(self, args):
		'''Install a target package from storage.
		usage: install <LOCAL_APK_PATH>
		Ex:
		 install /home/admin/app.apk
		 install app.apk
		'''
		cmd = args.split()
		cmd_l = len(cmd)
		if not args:
			print("Please provide a package name.")
		elif cmd_l == 1:
			if ".apk" in cmd[0][-4:]:
				pt.proc(f"Trying to install '{cmd[0]}' in target device.")
				c, st, sd = mt.exec_cmd(f"adb install {cmd[0]}", use_sh=True)
				if c == 0:
					pt.success(f"Package '{cmd[0]}' was installed.")
				else:
					pt.fail(f"Package '{cmd[0]}' couldnt be installed: {st}")
		elif cmd_l > 1:
			print(f"Too many args, use {cl.RED}help install{cl.RESET}.")
		else:
			print(f"Unknown instructions, use {cl.RED}help install{cl.RESET}.")
		return
		
	def do_sysinf(self, args):
		'''Shows device informations.'''
		sys_dict = mt.sysinf()
		if sys_dict:
			for i, v in sys_dict.items():
				print(f"{cl.GREEN}{i}{cl.RESET}: {v}")
		else:
			pt.fail("System informations are not accessible.")
				
	def do_getpro(self, args):
		'''Get device properties.'''
		r = subprocess.run(
			f"adb shell getprop",
			shell=True,
			capture_output=True,
			text=True
		)
		if r.returncode == 0:
			pt.success("")
			print(r.stdout)
		else:
			pt.fail(r.stderr)
	
	def do_shell(self, args):
		'''Open a raw shell in the target.'''
		subprocess.run("adb shell", shell=True, text=True)		
			
	def do_send(self, args):
		'''Send an file to the target.
		usage: send <LOCAL_PATH> <TARGET_PATH>
		Ex:
		 send file.dat /sdcard/
		 send /home/admin/app.apk /sdcard/Download/
		'''
		cmd = args.split()
		cmd_l = len(cmd)
		if cmd_l == 2:
			try:
				paths = [Path(cmd[0]).resolve(), Path(cmd[1]).resolve()]
			except Exception as e:
				pt.error(str(e))
			r = subprocess.run(f"adb push {cmd[0]} {cmd[1]}", shell=True, text=True)
			if r.returncode == 0:
				pt.success(f"File '{cmd[0]}' was sent to the target.")
			else:
				pt.fail(f"File '{cmd[0]}' couldnt be send the target.")
		elif cmd_l < 2:
			print(f"Too few args, use {cl.RED}help send{cl.RESET}.")
		elif cmd_l > 2:
			print(f"Too many args, use {cl.RED}help send{cl.RESET}.")
				
	def do_logcat(self, args):
		'''Displays target device logcat.'''
		subprocess.run("adb logcat -L", shell=True, text=True)
		
	def do_list_pkgs(self, args):
		'''List all device packages.
		usage: list <OPTIONS>
		Ex:
		 list
		 list search termux
		'''
		cmd = args.split()
		cmd_l = len(cmd)
		if cmd_l == 0:
			c, st, sd = mt.exec_adb("shell pm list packages")
			if c == 0:
				pt.success("")
				try:
					for line in sd.splitlines():
						_f = line.split(":")
						print(_f[1])
						sleep(0.005)
				except KeyboardInterrupt:
					return
			else:
				pt.fail(f"Cant list packages: {st}")
		elif cmd_l == 2 and cmd[0] == "search":
			c, st, sd = mt.exec_cmd(f"adb shell pm list packages | grep {cmd[1]}", use_sh=True)
			if c == 0:
				pt.success("")
				for line in sd.splitlines():
					_f = line.split(":")
					print(_f[1])
			else:
				pt.fail(f"Cant find string '{cmd[1]}'.")
		elif cmd_l > 2:
			print(f"Too many args, use {cl.RED}help list_pkgs{cl.RESET}.")
		else:
			print(f"Unknown instructions, use {cl.RED}help list_pkgs{cl.RESET}.")
		
	def do_start_app(self, package_name):
		'''Starts a application on target by package name.
		usage: start_app <PACKAGE_NAME>
		Ex:
		 start_app com.termux
		 start_app com.whatsapp
		'''
		cmd = package_name.split()
		cmd_l = len(cmd)
		if cmd_l == 1:
			mainget = subprocess.run(
				f"adb shell dumpsys package {cmd[0]} | grep -A 1 'MAIN'",
				shell=True, 
				capture_output=True, 
				text=True
			)
			if mainget.returncode == 0:
				string = str(mainget.stdout)
				searcher = string.find('/')
				grep = string[searcher:]
				grep2 = grep.find(' ')
				final_str = grep[:grep2].replace('/', '')
				r = subprocess.run(
					f"adb shell am start -n {cmd[0]}/{final_str}", 
					shell=True, 
					capture_output=True, 
					text=True
				)
				if r.returncode == 0:
					pt.success(f"App '{cmd[0]}' started.")
				else:
					pt.fail(f"App '{cmd[0]}' couldnt be started.")
			else:
				pt.fail("The program couldnt get package >MAIN<.")
		elif cmd_l > 1:
			print(f"Too many args, use {cl.RED}help start_app{cl.RESET}.")
		elif cmd_l < 1:
			print(f"Too few args, use {cl.RED}help start_app{cl.RESET}.")
		return
		
	def do_dump(self, args):
		'''Dump a target device file to your device.
		usage: dump <TARGET_PATH> <LOCAL_PATH>
		Ex:
		 send /sdcard/file.dat /home/admin/
		 send /sdcard/Download/app.apk /home/admin/
		'''
		cmd = args.split()
		cmd_l = len(cmd)
		if cmd_l == 2:
			try:
				paths = [Path(cmd[1]).resolve(), Path(cmd[0]).resolve()]
			except Exception as e:
				pt.error(str(e))
			r = subprocess.run(f"adb pull {cmd[0]} {cmd[1]}", shell=True, text=True)
			if r.returncode == 0:
				pt.success(f"File '{cmd[0]}' was dumped to '{cmd[1]}'.")
			else:
				pt.fail(f"File '{cmd[0]}' cant be dumped.")
		elif cmd_l < 2:
			print(f"Too few args, use {cl.RED}help dump{cl.RESET}.")
		elif cmd_l > 2:
			print(f"Too many args, use {cl.RED}help dump{cl.RESET}.")
		return
				
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
		Path(f"adb_dumps/{self.device}").mkdir(parents=True, exist_ok=True)
		if not args:
			print(f"Please provide args, or use {cl.RED}help dump_sd{cl.RESET}."); return
		cmd = args.split()
		cmd_l = len(cmd)
		if "," in cmd[0] and cmd_l == 1:
			items = cmd[0].split(",")
			_format = mt.formater(items)
			c, st, sd = mt.exec_cmd(f"adb shell find /sdcard/ | grep -iE \"({_format})\"", use_sh=True)
			if c == 0:
				try:
					for item in sd.splitlines():
						p = Path(item).resolve().suffix
						_type = mt.get_file_type(p)
						full_path = f"adb_dumps/{self.device}/{_type}/"
						Path(f"adb_dumps/{self.device}/{_type}").mkdir(parents=True, exist_ok=True)
						pt.proc(f"Dumping '{item}'.")
						c1, st1, sd1 = mt.exec_cmd(f"adb pull {item} {full_path}")
						if c1 == 0:
							pt.success(f"File '{item}' was dumped to '{full_path}'.")
				except KeyboardInterrupt:
					pt.success(f"Dumping process ended, visit 'adb_dumps/{self.device}' to find your dumps.")
				except Exception as e:
					pt.error(str(e))
		elif "," not in args and cmd_l == 1:	
			i = "."+cmd[0] if "." not in cmd[0] else cmd[0]
			c, st, sd = mt.exec_cmd(f"adb shell find /sdcard/ | grep -iE \"(\\{i})\"", use_sh=True)
			if c == 0:
				try:
					for item in sd.splitlines():
						p = Path(item).resolve().suffix
						_type = mt.get_file_type(p)
						full_path = f"adb_dumps/{self.device}/{_type}/"
						Path(full_path).mkdir(parents=True, exist_ok=True)
						pt.proc(f"Dumping '{item}'.")
						c1, st1, sd1 = mt.exec_cmd(f"adb pull {item} {full_path}")
						if c1 == 0:
							pt.success(f"File '{item}' was dumped to '{full_path}'.")
				except KeyboardInterrupt:
					pt.success(f"Dumping process ended, visit 'adb_dumps/{self.device}' to find your dumps.")
				except Exception as e:
					pt.error(str(e))
		elif cmd_l < 1:
			print(f"Too few args, use {cl.RED}help dump_sd{cl.RESET}.")
		elif cmd_l > 1:
			print(f"Too many args, use {cl.RED}help dump_sd{cl.RESET}.")
				
	def do_dump_wpp(self, args):
		'''Try dump high priority whatsapp data.'''
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
			for path in wpp_dirs:
				pt.proc(f"Trying dump '/sdcard/Android/media/com.whatsapp/WhatsApp/Media/{path}/'. ")
				c, st, sd = mt.exec_adb(
					f"pull \"/sdcard/Android/media/com.whatsapp/WhatsApp/Media/{path}/\" {str(base_p)}"
				)
				if c == 0:
					pt.success(f"Path '/sdcard/Android/media/com.whatsapp/WhatsApp/Media/{path}/' dumped.")
				else:
					pt.fail(f"Path '/sdcard/Android/media/com.whatsapp/WhatsApp/Media/{path}/' couldnt be dumped, attempting again...")	
					c1, st1, sd1 = mt.exec_adb(f"pull \"/sdcard/Android/media/com.whatsapp/WhatsApp/Media/{path}/\" {str(base_p)}")
					if c1 == 0:
						pt.success(f"Path '/sdcard/Android/media/com.whatsapp/WhatsApp/Media/{path}/' dumped.")
					else:
						pt.fail(f"Path '/sdcard/Android/media/com.whatsapp/WhatsApp/Media/{path}/' cant be dumped.")
			files = [p for p in base_p.rglob("*") if p.is_file()]
			for src_path in files:
				_format = mt.get_file_type(src_path.suffix)
				dest = base_p / f"{_format}"
				dest.mkdir(parents=True, exist_ok=True)
				dest_file = dest / src_path.name
				try:
					if dest_file.exists():
						if mt.file_hash(src_path) == mt.file_hash(dest_file):
							continue
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
					subprocess.run(
						f"adb shell screenrecord /sdcard/{filename}",
						shell=True, 
						text=True
					)
				except KeyboardInterrupt:
					sleep(3)
					s = subprocess.run(
						f"adb pull /sdcard/{filename} adb_dumps/{self.device}",
						shell=True,
						capture_output=True,
						text=True
					)
					if s.returncode == 0:
						pt.success(f"File '{filename}' was saved on adb_dumps/{self.device}.")
						q = pt.question("Do you want to open this recording?(y/n): ")
						if q.lower() == "y":
							mt.open_file(f"adb_dumps/{self.device}/{filename}")
						else:
							return
			except Exception as e:
				print(str(e))
		else:
			print(f"You dont need {cl.RED}args{cl.RESET}.")
			
	def do_screencap(self, args):
		'''Take a screenshot of the target device.
		usage: screencap
		'''
		if not args:
			filename = f"SCREENSHOT_{mt.get_time()}.png"
			try:				
				r = subprocess.run(
					f"adb shell screencap /sdcard/{filename}",
					shell=True, 
					text=True
				)
				if r.returncode == 0:
					s = subprocess.run(
						f"adb pull /sdcard/{filename} adb_dumps/{self.device}",
						shell=True,
						capture_output=True,
						text=True
					)
					if s.returncode == 0:
						pt.success(f"File '{filename}' was saved on adb_dumps/{self.device}.")
						q = pt.question("Do you want to open this screenshot?(y/n): ")
						if q.lower() == "y":
							mt.open_file(f"adb_dumps/{self.device}/{filename}")
						else:
							return
			except Exception as e:
				print(str(e))
		else:
			print(f"You dont need {cl.RED}args{cl.RESET}.")
		
	def do_ls(self, args):
		'''Lists folders and content.
		usage: ls <PATH>
		Ex:
		 ls
		 ls /
		'''
		cmd = args.split()
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
		elif cmd_l > 1:
			print(f"Too many args, use {cl.RED}help ls{cl.RESET}.")
		
	def do_cat(self, args):
		'''Shows files content
		usage: cat <FILE_PATH>
		Ex:
		 cat /etc/os-release
		'''
		cmd = args.split()
		cmd_l = len(cmd)
		if cmd_l == 1:
			file_path = Path(cmd[0]).resolve()
			try:
				c, d = mt.read_c(file_path)
				if c == 0:
					pt.success(f"'{file_path}':")
					print(d)
				else:
					pt.fail(f"Error while reading content: {d}")
			except TypeError:
				pt.fail(f"The file '{file_path}' dont exists.")
		elif cmd_l < 1:
			print(f"Too few args, use {cl.RED}help cat{cl.RESET}.")
		elif cmd_l > 1:
			print(f"Too many args, use {cl.RED}help dump{cl.RESET}.")
			
	def do_wipe(self, args):
		'''Wipe any file on target device.
		usage: wipe <TARGET_PATH>
		Ex:
		 wipe /sdcard/file.mp4
		'''
		cmd = args.split()
		cmd_l = len(cmd)
		if cmd_l == 1 and "/sdcard/" in cmd[0]:
			if mt.check_rm_sh():
				c, st, sd = mt.exec_cmd(
					f"adb shell sh /sdcard/rm.sh {cmd[0]}",
				)
				if c == 0:
					pt.success(f"File '{cmd[0]}' deleted from device storage.")
				else:
					pt.fail(f"File '{cmd[0]}' cant be deleted: {st}")
			else:
				c1, st1, sd1 = mt.exec_cmd(
					"adb push rm.sh /sdcard/"
				)
				if c1 == 0 and mt.check_rm_sh():
					c2, st2, sd2 = mt.exec_cmd(
						f"adb shell sh /sdcard/rm.sh {cmd[0]}",
					)
					if c2 == 0:
						pt.success(f"File '{cmd[0]}' deleted from device storage.")
					else:
						pt.fail(f"File '{cmd[0]}' cant be deleted: {st2}.")
				else:
					pt.fail("Couldnt send script 'rm.sh' to '/sdcard/'.")
		elif cmd_l > 1:
			print(f"Too many args, use {cl.RED}help wipe{cl.RESET}.")
		elif cmd_l < 1:
			print(f"Too few args, use {cl.RED}help wipe{cl.RESET}.")
		else:
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
		
if __name__ == "__main__":
	d = mt.check_device()
	if mt.check_if_linux():
		if mt.check_adb():
			if d:
				mt.check_paths(d)
				AdbRipper().cmdloop()
			else:
				print("No device conected.")
		else:
			print("Setuping ADB...")
	else:
		print("ADB Ripper just runs in linux.")
			
