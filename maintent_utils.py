import re
import shlex
import hashlib
import platform
from os import system
from pathlib import Path
from subprocess import run
from datetime import datetime

class Maintenance:
	
    @staticmethod
    def read_c(path):
        p = Path(path)
        try:
            if p.exists() and p.is_file():
                data = p.read_text()
                return 0, data
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
            return e
            
    @staticmethod
    def file_hash(path):
        h = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
	    
    @staticmethod
    def get_file_type(file_type):
        type_dict = {
            'fonts': ["otf","ttf"],
            'package': ["zip", "7z", "tar"],
            'exec': ["apk", "xapk", "exe"],
            'image': ["jpg", "png", "webp", "gif", "jpeg", "svg", "heic"],
            'text': ["txt", "csv", "dat", "log", "json", "xml"],
            'document': ["pdf", "xslx", "doc", "docx", "odt", "rtf"],
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
            
        elif "." in file_type:
            spliter = file_type.split(".")
            for item in spliter:
                for ty, value in type_dict.items():
                    if item in value:
                        return ty
    
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
    def exec_cmd(command, use_sh=False, timeout=60):
        try:
            if use_sh:
                cmd = command if isinstance(command, str) else " ".join(command)
            else:
                cmd = command if isinstance(command, list) else shlex.split(command)

            sub = run(
                cmd,
                shell=use_sh,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return (
                sub.returncode,
                sub.stderr.strip() if sub.stderr else "",
                sub.stdout.strip() if sub.stdout else ""
            )

        except Exception as e:
            return (1, str(e), "")
            
    @staticmethod
    def check_rm_sh():
        c, st, sd = Maintenance.exec_cmd(
            "adb shell ls /sdcard/rm.sh",
            use_sh=True
        )
        if c == 0:
            return True

    @staticmethod
    def exec_adb(command):
        return Maintenance.exec_cmd(f"adb {command}")

    @staticmethod
    def check_if_linux():
        sys = platform.system()
        if sys == "Linux":
            try:
                p = Path("/etc/os-release").read_text()
                mt = re.search(r'^ID_LIKE="?([^"\n]+)"?', p, re.MULTILINE)
                if mt:
                    return ("Linux", mt.group(1).strip())
            except Exception:
                pass
            return ("Linux", platform.node())
        return ("Not Linux", None)

    @staticmethod
    def check_adb():
        check = Maintenance.check_if_linux()
        if check[0] != "Linux":
            return False

        code, _, _ = Maintenance.exec_cmd("which adb")
        if code == 0:
            return True

        distro = check[1].lower() if check[1] else ""

        if "fedora" in distro:
            code, _, _ = Maintenance.exec_cmd(
                "sudo dnf install -y android-tools",
                use_sh=True
            )
            return code == 0
            
        if "archlinux" in distro:
            code, _, _ = Maintenance.exec_cmd(
                "sudo pacman -Syu --noconfirm android-tools",
                use_sh=True
            )
            return code == 0

        if "debian" in distro or "ubuntu" in distro:
            code, _, _ = Maintenance.exec_cmd(
                "sudo apt update && sudo apt install -y adb",
                use_sh=True
            )
            return code == 0

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

        c1, _, _ = Maintenance.exec_adb(
            "shell ls /sdcard/Android/media/com.whatsapp"
        )
        if c1 != 0:
            return False

        c2, _, sd2 = Maintenance.exec_adb(
            "shell ls /sdcard/Android/media/com.whatsapp/WhatsApp"
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
            c, st, sd = Maintenance.exec_cmd(value, use_sh=True)
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
    def check_key(key):
        return key.isdigit() and int(key) < 286

    @staticmethod
    def check_text(text):
        return isinstance(text, str) and len(text) >= 10

    @staticmethod
    def clear():
       system("clear")
