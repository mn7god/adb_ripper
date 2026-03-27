import re
import shlex
import shutil
import random
import hashlib
import platform
from pathlib import Path
from subprocess import run
from datetime import datetime
from os import system, remove, getenv
from collections import Counter


class Maintenance:
    
    @staticmethod
    def check_text(text):
        return isinstance(text, str) and len(text) > 0
    
    @staticmethod
    def check_regex(pattern, text):
        return re.search(pattern, text) is not None

    @staticmethod
    def return_sorted_dict(d: dict):
        return {c: v for c, v in sorted(d.items())}

    @staticmethod
    def read_c(path):
        p = Path(path)
        try:
            if p.exists() and p.is_file(): 
                return 0, p.read_text()
        except Exception as e:
            return 1, str(e)
            
    @staticmethod
    def path_runner(path):
        paths = []
        p = Path(path)
        try:
            if p.exists() and p.is_dir():
                for path in p.glob("*"):
                    paths.append(path)
            return paths
        except Exception as e:
            return None
            
    @staticmethod
    def file_hash(path):
        h = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
        
    @staticmethod
    def get_file_type(ft):
        file_type = ft.lower().lstrip(".")
        type_dict = {
            'fonts': ["otf","ttf"],
            'package': ["zip", "7z", "tar"],
            'exec': ["apk", "xapk", "exe"],
            'image': ["jpg", "png", "webp", "gif", "jpeg", "svg", "heic"],
            'text': ["txt", "csv", "dat", "log", "json", "xml"],
            'document': ["pdf", "xlsx", "doc", "docx", "odt", "rtf"],
            'video': ["mp4", "mkv", "avi", "mov"],
            'audio': ["mp3", "ogg", "m4a", "opus"],
            'script': ["sh", "py", "js", "php", "c", "cpp", "html"]
        }
        it = {}
        if "," in file_type:
            spliter = file_type.split(",")
            for item in spliter:
                for ty, value in type_dict.items():
                    if item in value:
                        it[item] = ty
            return it
            
        else:
            for ty, exts in type_dict.items():
                if file_type in exts:
                    return ty
            return None

    @staticmethod
    def get_time():
        return datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

    @staticmethod
    def formater(a_list):
        return "|".join(fr"\.{ext}" for ext in a_list)

    @staticmethod
    def f_reader(file: Path):
        try:
            if file.exists() and file.is_file():
                return file.read_text(), None
            return None, "File not found"
        except Exception as e:
            return None, str(e)

    @staticmethod
    def exec_cmd(command, shell=False, timeout=60):
        try:
            if shell:
                if not isinstance(command, str):
                    raise ValueError("shell=True requer string")
                cmd = command
            else:
                if isinstance(command, str):
                    cmd = shlex.split(command)
                else:
                    cmd = command
    
            sub = run(
                cmd,
                shell=shell,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )
    
            return sub.returncode, sub.stderr, sub.stdout
    
        except Exception as e:
            return 1, str(e), ""
            
    @staticmethod
    def check_rm_sh():
        c, st, sd = Maintenance.exec_cmd(
            ["adb", "shell", "ls", "/sdcard/rm.sh"]
        )
        return c == 0
        
    @staticmethod
    def check_if_linux():
        return platform.system() == "Linux"

    @staticmethod
    def check_adb():
        check = Maintenance.check_if_linux()
        if not check:
           return False

        code, _2, _1 = Maintenance.exec_cmd("which adb")
        if code == 0:
           return True

        return False

    @staticmethod
    def check_devices():
        code, _, stdout = Maintenance.exec_cmd("adb devices")
        if code != 0:
            return None
        
        devices = []

        lines = stdout.splitlines()
        for line in lines[1:]:
            if "\tdevice" in line:
                devices.append(line.split("\t")[0])

        return devices

    @staticmethod
    def check_paths():
        for device in Maintenance.check_devices():
            for path in ("adb_payloads", "adb_dumps", f"adb_dumps/{device}"):
                Path(path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def return_sessions():
        devices = Maintenance.check_devices()
        sessions = {}
        for device in devices:
            c, st, sd = Maintenance.exec_cmd(["adb", "-s", device, "shell", "uname", "-sm"])
            if c == 0 and sd:
                sessions[device] = sd

        return sessions

    @staticmethod
    def check_path(path: Path):
        return path.exists()

    @staticmethod
    def check_int(integer):
        try:
            int(integer)
            return True
        except ValueError:
            return False

    @staticmethod
    def check_key(key):
        return Maintenance.check_int(key) and int(key) < 287 and int(key) >= 0

    @staticmethod
    def clear():
       system("clear")

    @staticmethod
    def check_default_adbp(path: Path):
        conditions = [
            path.exists(),
            path.is_file(),
            path.suffix == ".adbp"
        ]
        if all(conditions):
            count = 0
            data = path.read_text()
            data_splited = data.splitlines()
            text = "adbpayload-description="
            re_1 = re.findall(text, data)
            
            if len(re_1) != 1:
                return False, ""
                
            if len(data_splited) < 4:
                return False, ""
                
            for l in data_splited:
                if re.match(r"\d{1}", l) or re.match(r"[a-zA-Z]", l):
                    count = 1;break
                    
            if count == 0:
                return False, ""

            for line in data_splited:
                if line.startswith(text) and Counter(line)["="] == 1:
                    a = line[len(text):]

            try:
                return True, a
            except UnboundLocalError:
                return False, ""

        return False, ""

    @staticmethod
    def check_input_events(custom_path: Path):
        status = Maintenance.check_default_adbp(custom_path)[0]
        input_events = []
        skip_flags = ("## File created by adb_ripper", "adbpayload-description=")
        
        if status:
            data = custom_path.read_text()
            input_events = [line for line in data.splitlines() if not line.startswith(skip_flags)]

        return status, input_events
    
    @staticmethod
    def list_adbp():
        files = {}
        path = Path("adb_payloads")
        
        for p in path.glob("*.adbp"):
            desc = Maintenance.check_default_adbp(p)
            if desc[0]:
                files[p.name] = [p, desc[1].strip()]
                
        return files
        
    @staticmethod
    def simple_list_adbp():
        files = []
        path = Path("adb_payloads")
        
        for p in path.glob("*.adbp"):
            desc = Maintenance.check_default_adbp(p)
            if desc:
                files.append(p.name)
                
        return files
    
    @staticmethod
    def payload_formatter(dictio: dict):
        init_list = []
        
        for key, value in dictio.items():
            init_list.append([key, value[1]])

        return init_list
        
    @staticmethod
    def sessions_formatter(dictio: dict):
        init_list = []
        
        for key, value in dictio.items():
            init_list.append([key] + [v for v in value.split()])

        return init_list
        
    @staticmethod
    def _generator(quantity: int):
        if quantity > 1:
            l = [str(random.randint(0,999)) for i in range(quantity)]
            return l
        elif quantity == 1:
            l = [str(random.randint(0,286)) for i in range(1)]
            return l
        
    @staticmethod
    def _input_format(input_list: list[int]):
        l = [str(i) for i in range(input_list)]
        return " ".join(l)
        
    @staticmethod
    def make_html(device, path, dest: Path):
        base_html = '''<!DOCTYPE html>
<html>
	<head>
		<meta name="author" content="mn7god">
		<meta name="keywords" content="adb,pwn,android">
		<meta name="X-UA-Compatible" content="ie=edge">
		<title>ADB Ripper Live Screen</title>
	</head>
	<body>
		<h1 style="text-align: center;">ADB Ripper Live Session: {}</h1>
        <div style="text-align: center;">
            <img src={} alt="ScreenCast" style="width: 100%; max-width: 800px; height: auto; display: block; margin: 0 auto;"></img>
        </div>
		<script>
			setInterval(function() {}, 1000);
		</script>
	</body>
</html>'''.format(device, path, "{location.reload();}")
        if not dest.exists() and not dest.is_dir():
            dest.write_text(base_html)
        elif dest.exists() and dest.is_file():
            remove(dest)
            dest.write_text(base_html)
    
    @staticmethod
    def detect_termux():
        e = getenv("HOME")
        if 'com.termux' in e:
            return True
        return False
    
    @staticmethod
    def open_file(file_name):
        mt = Maintenance
        if mt.detect_termux():
            mt.exec_cmd(["termux-open-url", file_name])
        
        mt.exec_cmd(["xdg-open", file_name])
        
    @staticmethod
    def check_path_traversal(path: str):
        black_list = ["../", "..//", "\\..", "\\..", "/..", "//.."]
        for i in black_list:
            if i in path:
                return True;break
                
    @staticmethod
    def dangerous_strings(text: str):
        black_list = ["&&", ";", "||", "|"]
        for i in black_list:
            if i in text:
                return True;break
            
