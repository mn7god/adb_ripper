import re
import shlex
import subprocess
from time import sleep
from pathlib import Path
from itertools import cycle
from tabulate import tabulate
from .printit import Color as cl
from .printit import PrintIt as pt
from .maintenance_utils import Maintenance as mt
from concurrent.futures import ThreadPoolExecutor

PKG_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$")
SWIPE_RE = re.compile(r"(?:0|[1-9]\d{0,3}) (?:0|[1-9]\d{0,3}) (?:0|[1-9]\d{0,3}) (?:0|[1-9]\d{0,3})")
TAP_RE = re.compile(r"(?:0|[1-9]\d{0,3}) (?:0|[1-9]\d{0,3})")
URL_RE = re.compile(r'^(https?://)?([a-zA-Z0-9.-]+|\d{1,3}(\.\d{1,3}){3})(:\d+)?(/[^\s]*)?$')

class AdbSession:
    def __init__(self, device: str):
        if not device:
            raise ValueError("Need to specify a device.")
        self.device = device

    def _run(self, cmd):
        return mt.exec_cmd(["adb", "-s", self.device] + cmd)

    def check_wpp_path(self):

        c2, _, sd2 = self._run(
            ["shell", "ls", "/sdcard/Android/media/com.whatsapp/WhatsApp/Media"]
        )
        if c2 != 0 or not sd2.strip():
            return False

        return True

    def sysinf(self):
        sys_infos = {}

        sys_infos['Android Version'] = self._run(["shell", "getprop", "ro.build.version.release"])[2]
        sys_infos['Device Model'] = self._run(["shell", "getprop", "ro.product.model"])[2]
        sys_infos['Device Manufacturer'] = self._run(["shell", "getprop", "ro.product.manufacturer"])[2]
        sys_infos['SDK Number'] = self._run(["shell", "getprop", "ro.build.version.sdk"])[2]
        sys_infos['Firmware Fingerprint'] = self._run(["shell", "getprop", "ro.build.fingerprint"])[2]
        sys_infos['Kernel Info'] = self._run(["shell", "uname", "-a"])[2]

        c, st, sd = self._run(["shell", "dumpsys", "battery"])
        if c == 0 and sd:
            for line in sd.splitlines():
                line_s = line.strip()
                line_value = line_s.split(":")[-1]
                if "AC powered:" in line_s:
                    sys_infos['Charging'] = line_value
                elif "level:" in line_s:
                    sys_infos['Battery Level'] = line_value

        for key, value in mt.return_sorted_dict(sys_infos).items():
            print(f"""{cl.GREEN}{key}{cl.RESET}: '{value.strip().replace("'","")}'""")

    def send_text(self, text: str):
        _formated = text.replace(" ", "%s").replace("\t", "%s")

        c, st, sd = self._run(["shell", "input", "text", _formated])
        if c == 0:

            pt.success(f"Text '{text}' was sent to device '{self.device}'.");return

        pt.fail(f"Text '{text}' failed to reach device '{self.device}' input.")

    def send_key(self, key: str):
        if SWIPE_RE.fullmatch(key):
            args = shlex.split(key)
            c, st, sd = self._run(["shell", "input", "swipe", *args])
            if c == 0:
                pt.success(f"Swipe event '{key}' was sent to device '{self.device}'.");return

        elif TAP_RE.fullmatch(key):
            args = shlex.split(key)
            c, st, sd = self._run(["shell", "input", "tap", *args])
            if c == 0:
                pt.success(f"Tap event '{key}' was sent to device '{self.device}'.");return

        elif mt.check_key(key):
            c, st, sd = self._run(["shell", "input", "keyevent", key])
            if c == 0:
                pt.success(f"Key event '{key}' was sent to device '{self.device}'.");return

        elif key == "":
            c, st, sd = self._run(["shell", "input", "press"])
            if c == 0:
                pt.success(f"Press event was sent to device '{self.device}'.");return

        elif " " in str(key) or not key.isdigit():
            self.send_text(key);return

        pt.fail(f"Key '{key}' cant be sent to device '{self.device}'.")

    def multikey(self, keys: list[str]):
        for item in keys:
            self.send_key(item)

    def search(self, term: str):
        if "*" not in term and "?" not in term:
            term = f"*{term}*"

        if mt.dangerous_strings(term):
            pt.error("Dangerous strings detected, aborting...");return

        c, st, sd = self._run(["shell", "find", "/sdcard/", "-type", "f", "-name", term])

        if c == 0 and sd:
            pt.success(f"Found {len(sd.splitlines())} ocurrences with term '{term}' in '{self.device}':")
            for line in sd.splitlines():
                print(line)
            return
        else:
            pt.fail(f"0 Ocurrences with term '{term}' on '{self.device}'.");return

        pt.fail(f"Failed to fetch files in device '{self.device}'.")

    def ripper(self, mode: str, payload=None, delay=2):

        if mode == "list":
            payloads = mt.list_adbp()
            if payloads != {}:
                _payload_format = mt.payload_formatter(payloads)
                print(tabulate(_payload_format, headers=["Payload Name", "Description"], tablefmt="simple_grid"));return

            pt.fail("None payloads found in 'adb_payloads' path.")

        elif mode == "run" and isinstance(payload, str):
            adbp_list = mt.list_adbp()
            keys = adbp_list.keys()
            delay = delay if delay < 60 and delay > -1 else 2
            if payload in keys:
                events = mt.check_input_events(Path(f"{adbp_list[payload][0]}"))

                if events[0] and events[1]:
                    for item in events[1]:
                        self.send_key(item)
                        sleep(delay)
                else:
                    pt.fail("Invalid payload content.")

                return

            pt.fail(f"Payload '{payload}' dont exists in 'adb_payloads' path.")

    def clear_package(self, pkg: str):
        if PKG_RE.match(pkg):
            r = pt.yes_no(f"Package '{pkg}' data will be wiped, do you want to proceed?")
            if r:
                c, st, sd = self._run(["shell", "pm", "clear", pkg])
                if c == 0:
                    pt.success(f"Package '{pkg}' data wiped.");return

                pt.fail(f"Failed to wipe '{pkg}' data.")

            else:
                pt.fail("User aborted.")

    def send(self, local: str, remote: str):
        src = Path(local)

        if not src.exists() or not src.is_file():
            pt.error(f"Local file not found: '{local}'")
            return

        if not remote.startswith("/sdcard/"):
            pt.error("Remote path must start with '/sdcard/'")
            return

        if mt.check_path_traversal(remote):
            pt.error("Path traversing detected, aborting...")
            return

        c, st, sd = self._run(["push", str(src), remote])

        if c == 0:
            pt.success(f"Sent '{local}' -> '{self.device}:{remote}'")
        else:
            pt.fail(f"Push failed: {st or sd}")

    def dump(self, remote: str, local: str):
        dest = Path(local)

        if not remote.startswith("/sdcard/"):
            pt.fail("Remote path must start with '/sdcard/'")
            return

        dest.mkdir(parents=True, exist_ok=True)

        c, st, sd = self._run(["pull", remote, str(dest)])

        if c == 0:
            pt.success(f"Dumped '{self.device}:{remote}' -> '{local}'")
        else:
            pt.fail(f"Pull failed: {st or sd}")

    def uninstall(self, pkg: str):
        if PKG_RE.match(pkg):
            r = pt.yes_no(f"Package '{pkg}' will be removed from device if it exists, do you want proceed?")
            if r:
                c, st, sd = self._run(["uninstall", pkg])
                if c == 0:
                    pt.success(f"Package '{pkg}' uninstalled.");return

                pt.fail(f"Failed to delete '{pkg}' from device '{self.device}'.")

            else:
                pt.fail("User aborted.")

    def force_stop(self, pkg: str):
        if PKG_RE.match(pkg):
            c, st, sd = self._run(["shell","am","force-stop",pkg])
            if c == 0:
                pt.success(f"Package '{pkg}' stoped.");return

            pt.fail(f"Failed to stoped '{pkg}' from device '{self.device}'.")

    def send_msg(self, text: str):
        c, st, sd = self._run(["shell","cmd","notification","post",'"MSG"',f'\"{text}\"'])
        if c == 0:
            pt.success(f"Message '{text}' was sent to device '{self.device}'");return

        pt.fail(f"Failed to send message '{text}' to device '{self.device}'.")

    def send_msg_spam(self, msg=None):
        if msg != None:
            try:
                input("Press ENTER to start attack, CTRL + C to stop.")
                while True:
                    s = mt.get_random_string()
                    c, st, sd = self._run(["shell","cmd","notification","post",f'"{s}"',f'\"{msg}\"'])
                    if c == 0:
                        pt.success(f"Message '{msg}' was sent to device '{self.device}'")
                    else:
                        pt.fail(f"Failed to send message '{msg}' to device '{self.device}'.")

            except KeyboardInterrupt:
                pt.proc("Spam stoped")
        else:
            try:
                input("Press ENTER to start attack, CTRL + C to stop.")
                while True:
                    msg = mt.get_random_string()
                    c, st, sd = self._run(["shell","cmd","notification","post",f'"{msg}"',f'\"{msg}\"'])
                    if c == 0:
                        pt.success(f"Message '{msg}' was sent to device '{self.device}'")
                    else:
                        pt.fail(f"Failed to send message '{msg}' to device '{self.device}'.")

            except KeyboardInterrupt:
                pt.proc("Spam stoped")
                
    def list_notifications(self):
        c, st, sd = self._run(["shell","cmd","notification","list"])
        apps = {}
        if c == 0 and sd:
            for line in sd.splitlines():
                c1, st1, sd1 = self._run(["shell","cmd","notification","get",line.replace("|","\\|")])
                if c1 == 0 and sd1:
                    for l in sd1.splitlines():
                         if "opPkg=" in l:
                            pt.success(f"APP: {l.split('=')[-1]}");break
                    s = re.search(r"extras=\{(.*?)\}", sd1, re.DOTALL)
                    if s:
                        c = s.group(1)
                        print(c.strip())

                    print("")

            return

        pt.fail(f"Failed to list notifications on device '{self.device}'.")

    def list_saved_networks(self):
        c, st, sd = self._run(["shell","cmd","wifi","list-networks"])
        if c == 0 and sd:
            pt.success(f"\n{sd}")
            return

        pt.fail(f"Failed to list saved networks on device '{self.device}'.")

    def force_stop_spam(self, pkgs: list):
        input("Press ENTER to start attack, CTRL + C to stop.")
        try:
            for pkg in cycle(pkgs):
                if PKG_RE.match(pkg):
                    c, st, sd = self._run(["shell","am","force-stop",pkg])
                    if c == 0:
                        pt.success(f"Package '{pkg}' stoped.")
                    else:
                        pt.fail(f"Failed to stop '{pkg}' from device '{self.device}'.")

        except KeyboardInterrupt:
            pt.proc("Spam stoped")

    def current_app(self):
        c, st, sd = self._run(["shell","dumpsys","activity","activities"])
        if c == 0 and "topResumedActivity" in sd:
            for line in sd.splitlines():
                if "topResumedActivity" in line:
                    splited = line.split(" ")[-2].replace("}","").split("/")
                    if len(splited) == 2:
                        pt.success(f"Current package name: {splited[0]}")
                        pt.success(f"Current package main: {splited[1]}")
            return
                  
        else:
            c1, st1, sd1 = self._run(["shell","dumpsys","window","windows"])
            if c1 == 0 and sd1:
                for line in sd1.splitlines():
                    if "mFocusedApp" in line or "mCurrentFocus" in line:
                        splited = line.split(" ")[-1].replace("}", "").split("/")
                        if len(splited) == 2:
                            pt.success(f"Current package name: {splited[0]}")
                            pt.success(f"Current package main: {splited[1]}")
                return
            
        pt.fail(f"Failed to get current app in device '{self.device}'.")

    def open_url(self, url: str):
        if URL_RE.fullmatch(url):
            c, st, sd = self._run(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d",url])
            if c == 0:
                pt.success(f"Started URL '{url}' in '{self.device}'.")
                return

            pt.fail(f"Failed to open '{url}' on device '{self.device}'.")
        else:
            pt.error("Invalid URL.")
            
    def swipe_spam(self, delay=0.1):
        while True:
            try:
                r = mt._generator(4)
                self.send_key(" ".join(r))
                sleep(delay)
            except KeyboardInterrupt:
                pt.proc("Spam stoped");break
                
    def tap_spam(self, delay=0.1):
        while True:
            try:
                r = mt._generator(2)
                self.send_key(" ".join(r))
                sleep(delay)
            except KeyboardInterrupt:
                pt.proc("Spam stoped");break
                
    def keyevent_spam(self, delay=0.1):
        while True:
            try:
                r = mt._generator(1)
                self.send_key(" ".join(r))
                sleep(delay)
            except KeyboardInterrupt:
                pt.proc("Spam stoped");break
    
    def press_spam(self, delay=0.1):
        while True:
            try:
                self.send_key("")
                sleep(delay)
            except KeyboardInterrupt:
                pt.proc("Spam stoped");break
                
    def brightness_spam(self):
        while True:
            try:
                r = mt.get_random_brightness_value()
                c, st, sd = self._run(["shell","cmd","display","set-brightness",f"{r}"])
                if c == 0:
                    pt.success(f"Brightness level '{r}' was sent to device.")

                sleep(1)
            except KeyboardInterrupt:
                pt.proc("Spam stoped");break
                
    def ui_spam(self, delay=0.1):
        for i in cycle(["yes","no"]):
            try:
                c, st, sd = self._run(["shell","cmd","uimode","night",i])
                if c == 0 and sd:
                    pt.success(f"Night UIMODE '{i}' was sent to device.")
            except KeyboardInterrupt:
                pt.proc("Spam stoped");break

            sleep(delay)
            
    def battery_stats_spam(self):
        while True:
            try:
                r = mt.get_random_battery_value()
                c, st, sd = self._run(["shell","cmd","battery","set","level",f"{r}"])
                if c == 0:
                    pt.success(f"Battery value '{r}' was sent to device.")
                sleep(1)
            except KeyboardInterrupt:
                pt.proc("Spam stoped")
                c1, st1, sd1 = self._run(["shell","cmd","battery","reset"])
                break
                
    def spam(self, mode=None, pkgs=None, msg=None):
        mode = mode.strip()
        
        input_spam = {
            "swipe-random": self.swipe_spam,
            "tap-random": self.tap_spam,
            "keyevent-random": self.keyevent_spam,
            "press-spam": self.press_spam
        }
        
        display_spam = {
            "brightness": self.brightness_spam,
            "ui": self.ui_spam,
            "battery": self.battery_stats_spam
        }
        
        force_stop_spam = {
            "force-stop": self.force_stop_spam
        }
        
        send_msg_spam = {
            "send-msg": self.send_msg_spam
        }
        
        if mode == None:
            pt.error("Unknown Mode")
        
        if input_spam.get(mode) != None:
            r = pt.yes_no("'input_spam' will send massive input events to device, do you want to proceed anyway?")
            if r:
                input_spam[mode]()
                
        elif display_spam.get(mode) != None:
            r = pt.yes_no("'display_spam' will send massive screen events to device, do you want to proceed anyway?")
            if r:
                display_spam[mode]()
                
        elif send_msg_spam.get(mode) != None:
            r = pt.yes_no("'send_msg_spam' will spam with a massive shell messages to device, do you want to proceed anyway?")
            if r:
                send_msg_spam[mode](msg)
                
        elif force_stop_spam.get(mode) != None and pkgs != None:
            r = pt.yes_no("'force_stop_spam' can harm device running packages, do you want to proceed anyway?")
            if r:
                force_stop_spam[mode](pkgs)

    def install(self, apk: str):
        if apk.endswith(".apk") and Path(str(apk)).exists():

            c, st, sd = self._run(["install", apk])
            if c == 0:
                pt.success(f"APK '{apk}' was installed on '{self.device}'.");return

        pt.fail(f"Cant install '{apk}' on '{self.device}'")

    def list_packages(self, term=None):
        c, st, sd = self._run(["shell", "pm", "list", "packages"])
        if c != 0 or not sd:
            pt.fail("Failed to get packages list.")
            return

        packages = [line.split(":")[-1].strip() for line in sd.splitlines()]

        if not term or not term.strip():
            pt.success("Available packages:")
            for pkg in packages:
                print(pkg)
            return

        found = []

        term = term.lower().strip()

        for pkg in packages:
            if term in pkg.lower():
                found.append(pkg)

        if found:
            pt.success("Packages found:")
            for f in found:
                print(f)
            return

        pt.fail("No packages matched.")

    def getprop(self, term=None):

        if not term:
            c, st, sd = self._run(["shell", "getprop"])
            if c == 0 and sd:
                pt.success("")
                for line in sd.splitlines():
                    print(line);sleep(0.01)
                return

        if mt.dangerous_strings(term):
            pt.error("Dangerous strings found in term value, aborting...")
            return

        c1, st1, sd1 = self._run(["shell", "getprop", term])
        if c1 == 0 and sd1:
            pt.success(f"{term}: {sd1}")
            return

        pt.fail(f"Failed to fetch device '{self.device}' propierties.")

    def shell(self):
        pt.proc(f"Attempting to open a shell on device '{self.device}'.")
        subprocess.run(["adb", "-s", self.device, "shell"])

    def start_app(self, pkg: str):
        if PKG_RE.match(pkg):
            c, st, sd = self._run(["shell", "monkey", "-p", pkg, "1"])
            if c == 0 and sd:
                pt.success(f"Started package '{pkg}' on '{self.device}'.");return

            pt.fail(f"Cant start package '{pkg}' on '{self.device}'.");return

        pt.fail(f"Failed to find package '{pkg}' in devices '{self.device}'.")

    def cmd(self, command: list):
        c, st, sd = self._run(["shell", "cmd"] + command)

        output = ""
        if sd:
            output += sd
        if st:
            output += st

        command = " ".join(command)

        if c == 0:
            pt.success(f"Command 'cmd {command}' executed in device '{self.device}':\n{output}");return
        elif c != 0:
            pt.fail(f"Command 'cmd {command}' cant be executed in device '{self.device}': {output}");return

        pt.fail(f"Failed to execute command 'cmd {command}' in device '{self.device}'.")

    def battery(self, command: list):
        c, st, sd = self._run(["shell", "cmd", "battery"] + command)

        output = ""
        if sd:
            output += sd
        if st:
            output += st

        command = " ".join(command)

        if c == 0:
            pt.success(f"Command 'battery {command}' executed in device '{self.device}':\n{output}");return
        elif c != 0:
            pt.fail(f"Command 'battery {command}' cant be executed in device '{self.device}': {output}");return

        pt.fail(f"Failed to execute 'cmd' command 'battery {command}' in device '{self.device}'.")

    def display(self, command: list):
        c, st, sd = self._run(["shell", "cmd", "display"] + command)

        output = ""
        if sd:
            output += sd
        if st:
            output += st

        command = " ".join(command)

        if c == 0:
            pt.success(f"Command 'display {command}' executed in device '{self.device}':\n{output}");return
        elif c != 0:
            pt.fail(f"Command 'display {command}' cant be executed in device '{self.device}': {output}");return

        pt.fail(f"Failed to execute 'cmd' command '{command}' in device '{self.device}'.")

    def screenrecord(self, remote: str):
        dest = f"adb_dumps/{self.device}/video"
        if len(remote) > 8:
            if not remote.startswith("/sdcard/"):
                remote = f"/sdcard/{remote}"
            if not remote.endswith(".mp4"):
                remote += ".mp4"
            Path(dest).mkdir(parents=True, exist_ok=True)
            try:
                pt.proc("Screen record started, press CTRL + C to stop.")
                subprocess.run(["adb", "-s", self.device, "shell", "screenrecord", remote])
            except KeyboardInterrupt:
                pt.proc("Process ended, dumping screenrecord...")
                sleep(5)
                self.dump(remote, dest)
            return

        pt.fail("Failed to fetch remote path.")

    def screencap(self, remote: str):
        dest = f"adb_dumps/{self.device}/image"
        if len(remote) > 8:
            if not remote.startswith("/sdcard/"):
                remote = f"/sdcard/{remote}"
            if not remote.endswith(".png"):
                remote += ".png"
            Path(dest).mkdir(parents=True, exist_ok=True)
            c, st, sd = self._run(["shell", "screencap", remote])
            if c == 0:
                self.dump(remote, dest)
            return

        pt.fail("Failed to take screenshot.")

    def screenshot(self, delay: int, dest: Path):
        remote = "/sdcard/screencast.png"
        while True:
            try:
                c, st, sd = self._run(["exec-out", "screencap", remote])
                if c == 0:
                    pt.success("Screnshot taken.")
                    self.dump(remote, dest)

                sleep(max(0.4, delay))
            except KeyboardInterrupt:
                pt.proc("Live interrupted");break

    def live(self):
        pt.proc("Creating index.html...")
        png = f"screencast.png"
        html = Path(f"adb_dumps/{self.device}/index.html")
        png_path = Path(f"adb_dumps/{self.device}/")

        try:
            mt.make_html(self.device, png, html)
            pt.success("Created 'index.html'.")
        except Exception as e:
            pt.fail(f"Failed to create index.html: {str(e)}");return

        tmx = mt.detect_termux()

        pt.proc("Starting live html in browser... press CTRL + C to stop.")

        if tmx:
            pt.fail("Live mode in termux isnt suported.")
        else:
            subprocess.run(["xdg-open", str(html)])
            self.screenshot(0.4, png_path)

    def dump_sd(self, extensions: tuple[str], workers=2):
        c, st, sd = self._run(["shell", "find", "/sdcard/", "-type", "f"])
        if c != 0:
            pt.fail(f"Failed to fetch files in '{self.device}'.");return

        exts = tuple([f".{ext.lstrip('.')}" for ext in extensions])

        for ext in exts:
            if mt.dangerous_strings(ext):
                pt.error("Dangerous strings in extensions, aborting...")
                break;return

        files = []

        for f in sd.splitlines():
            f = f.strip()
            if not f:
                continue

            try:
                if f.lower().endswith(exts):
                    files.append(f)
            except Exception:
                continue

        def worker(f):
            ext = Path(f).suffix
            dest = f"adb_dumps/{self.device}/{mt.get_file_type(ext)}"
            Path(dest).mkdir(parents=True, exist_ok=True)
            self.dump(f, str(dest))

        r = pt.yes_no(f"Your extensions matches with '{len(files)}' files from device storage, do you want dump all of them?")
        if r:
            with ThreadPoolExecutor(max_workers=workers) as exe:
                list(exe.map(worker, files))

            pt.success(f"Dumped {len(files)} files to 'adb_dumps/{self.device}'.")

        else:

            pt.fail("Dumping aborted.")

    def dump_wpp(self):
        files = []
        r = pt.yes_no("'dump_wpp' will make a massive adb server requests, do you want continue anyway?")
        if r:
            try:
                if not self.check_wpp_path():
                    pt.fail("WhatsApp media path not accessible.")
                    return
            
                base = Path(f"adb_dumps/{self.device}/WhatsApp")
                base.mkdir(parents=True, exist_ok=True)
                remote_base = "/sdcard/Android/media/com.whatsapp/WhatsApp/Media/"
                c, st, sd = self._run([
                    "shell", "find", remote_base, "-type", "f"
                ])

                if c != 0 or not sd:
                    pt.fail("No WhatsApp media files found.")
                    return

                files = [f.strip() for f in sd.splitlines()]
            
                for f in files:
                    self.dump(f, str(base))

            except KeyboardInterrupt:
                pt.success(f"Dumped {len(files)} files from '{self.device}' to '{base}'.");return
                
            pt.success(f"Dumped {len(files)} files from '{self.device}' to '{base}'.")
            
        else:
            pt.fail("Dump whatsapp data aborted.")

