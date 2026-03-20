import re
import shlex
import hashlib
import platform
import ipaddress
from os import system
from pathlib import Path
from subprocess import run
from datetime import datetime

class Maintenance:
    
    @staticmethod
    def check_regex(pattern, text):
        return re.search(pattern, text) is not None
        
    @staticmethod
    def check_ip(ip: str):
        try:
            ipaddress.ip_address(ip);return True
        except:
            return False
            
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
        # só aceita lista nesse formato: ','
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
    def open_file(file_name):
        Maintenance.exec_cmd(["xdg-open", file_name])

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
    def check_device():
        code, _, stdout = Maintenance.exec_cmd("adb devices")
        if code != 0:
            return None
        
        lines = stdout.splitlines()
        for line in lines[1:]:
            if "\tdevice" in line:
                return line.split("\t")[0]

        return None

    @staticmethod
    def check_paths(device):
        for path in ("adb_payloads", "adb_dumps", f"adb_dumps/{device}"):
            Path(path).mkdir(exist_ok=True)

    @staticmethod
    def check_wpp_path():
        if not Maintenance.check_device():
            return False

        wpp_dirs = {
            "WallPaper",
            "WhatsApp AI Media",
            "WhatsApp Animated Gifs",
            "WhatsApp Audio",
            "WhatsApp Backup Excluded Stickers",
            "WhatsApp Bug Report Attachments",
            "WhatsApp Documents",
            "WhatsApp Images",
            "WhatsApp Profile Photos",
            "WhatsApp Sticker Packs",
            "WhatsApp Stickers",
            "WhatsApp Video",
            "WhatsApp Video Notes",
            "WhatsApp Voice Notes",
        }

        c1, _, _ = Maintenance.exec_cmd(
            ["adb", "shell", "ls", "/sdcard/Android/media/com.whatsapp"]
        )
        if c1 != 0:
            return False

        c2, _, sd2 = Maintenance.exec_cmd(
            ["adb", "shell", "ls", "/sdcard/Android/media/com.whatsapp/WhatsApp"]
        )
        if c2 != 0:
            return False

        return True
    
    @staticmethod
    def sysinf():
        _items = {
            'Android Version': "adb shell getprop ro.build.version.release",
            'Battery Level': "adb shell dumpsys battery | grep level | cut -d' ' -f4",
            'Charging': "adb shell dumpsys battery | grep 'AC powered' | cut -d' ' -f5",
            'Device Model': "adb shell getprop ro.product.model", 
            'Device Manufacturer': "adb shell getprop ro.product.manufacturer",
            'SDK Number': "adb shell getprop ro.build.version.sdk",
            'Firmware Fingerprint': "adb shell getprop ro.build.fingerprint",
            'Kernel Info': "adb shell uname -a",
        }
        adb_info = {}
        for i, value in _items.items():
            c, st, sd = Maintenance.exec_cmd(value, shell=True)
            if c == 0:
                adb_info[i] = sd
        if adb_info:
            return adb_info
            
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
    def connect_device():
        mt = Maintenance
    
        device = input("Device IP: ").strip()
        pair_port = input("Pair port: ").strip()
        pair_code = input("Pairing code: ").strip()
        connect_port = input("Connect port: ").strip()
    
        # validações básicas
        if not mt.check_ip(device):
            print("Invalid IP address.")
            return False
    
        if not (mt.check_int(pair_port) and 1 <= int(pair_port) <= 65535):
            print("Invalid pair port.")
            return False
    
        if not mt.check_text(pair_code):
            print("Invalid pairing code.")
            return False
    
        if not (mt.check_int(connect_port) and 1 <= int(connect_port) <= 65535):
            print("Invalid connect port.")
            return False
    
        c, st, sd = mt.exec_cmd([
            "adb", "pair", f"{device}:{pair_port}", pair_code
        ])
    
        if c != 0 or "Successfully paired" not in sd:
            print(f"Pairing failed: {st or sd}")
            return False
    
        c1, st1, sd1 = mt.exec_cmd([
            "adb", "connect", f"{device}:{connect_port}"
        ])
    
        if c1 != 0 or "connected to" not in sd1:
            print(f"Connection failed: {st1 or sd1}")
            return False
    
        return True

    @staticmethod
    def check_key(key):
        return key.isdigit() and int(key) < 286

    @staticmethod
    def check_text(text):
        return isinstance(text, str) and len(text) > 0

    @staticmethod
    def clear():
       system("clear")
