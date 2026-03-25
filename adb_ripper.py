import re
import cmd2
import shlex
import argparse
import subprocess
from os import remove
from time import sleep
from pathlib import Path
from tabulate import tabulate
from adb_libs.printit import Color as cl
from adb_libs.printit import PrintIt as pt
from adb_libs.adb_session import AdbSession 
from adb_libs.cmd2_parsers import Parsers as prs
from adb_libs.maintenance_utils import Maintenance as mt

IP_RE = re.compile(r"^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$")
PORT_RE = re.compile(r"^(0|[1-9]{4,5})$")
PAIR_CODE_RE = re.compile(r"^([1-9]{1}[0-9]{5})$")

class AdbRipper(cmd2.Cmd):
    
    def __init__(self, no_intro=False):
        super().__init__()
        self.no_intro = no_intro
        if self.no_intro:
            self.intro = ""
        else:
            self.intro = pt.banner()
        self.prompt = f"{cl.WHITE_LINE}adbr{cl.RESET}> "
        
    @cmd2.with_argparser(prs.sessions_parser)
    def do_sessions(self, args):
        
        devices = mt.check_devices()
        
        if args.l:
            s = mt.return_sessions()
            if s != {}:
                table = mt.sessions_formatter(s)
                print(tabulate(table, headers=["Device","System","Kernel Release","Arch"], tablefmt="simple_grid"))
            else:
                pt.fail("No valid sessions online found.")

            return

        elif args.K:
            c, st, sd = mt.exec_cmd(["adb", "disconnect"])
            if c == 0:
                pt.success("All sessions killed");return
            
            pt.fail("Failed to kill all adb sessions.")

        elif args.L:
            if args.L in devices:
                SessionManager(args.L).cmdloop();return
            
            pt.fail(f"Device '{args.L}' not found.");return

        elif args.k:
            if args.k in devices:
                c, st, sd = mt.exec_cmd(["adb", "disconnect", args.k])
                if c == 0:
                    pt.success(f"Device '{args.k}' disconnected.");return
                    
        elif args.c:
            _ip, _port = args.c
            if IP_RE.fullmatch(_ip) and PORT_RE.fullmatch(_port):
                c, st, sd = mt.exec_cmd(["adb", "connect", f"{_ip}:{_port}"])
                if c == 0 and not "failed to connect" in sd.lower():
                    pt.success(f"Connection successfull with device IP '{_ip}'.");return
                
                pt.fail(f"Cant connect with device IP '{_ip}'.");return
                
        elif args.C:
            _ip, _ip_port, _pair_port, _pair_code = args.C
            condition = [
                IP_RE.fullmatch(_ip),
                PORT_RE.fullmatch(_ip_port),
                PORT_RE.fullmatch(_pair_port),
                PAIR_CODE_RE.fullmatch(_pair_code),
            ]
            if all(condition):
                c, st, sd = mt.exec_cmd(["adb", "pair", f"{_ip}:{_pair_port}", _pair_code])
                if c == 0 and not "error: protocol fault" in sd.lower():
                    pt.success(f"Paired successfully with device IP '{_ip}'.")
                    c1, st1, sd1 = mt.exec_cmd(["adb", "connect", f"{_ip}:{_ip_port}"])
                    if c1 == 0 and not "failed" in sd.lower():
                        pt.success(f"Connected successfully with device IP '{_ip}'");return
                    
                    pt.fail(f"Cant connect with device IP '{_ip}'.");return
                
                pt.fail(f"Cant pair with device IP '{_ip}'.");return

        pt.error(f"Unknown instructions please use '{cl.RED}help sessions{cl.RESET}'")
        
    def do_banner(self, arg):
        '''Displays a banner on the screen.'''
        pt.banner()
        
class SessionManager(AdbRipper):
    
    def __init__(self, device: str):
        super().__init__(no_intro=True)
        self.device = device
        if not self.device:
            raise ValueError("Need an specified device.")
        self.session = AdbSession(self.device)
        self.prompt = f"{cl.WHITE_LINE}session{cl.RESET}:{cl.DARK_GREEN}{self.device}{cl.RESET}> "
        mt.check_paths()
    
    @cmd2.with_argparser(prs.sessions2_parser)
    def do_sessions(self, args):
        
        devices = mt.check_devices()
        
        if args.l:
            s = mt.return_sessions()
            if s != {}:
                table = mt.sessions_formatter(s)
                print(tabulate(table, headers=["Device","System","Kernel Release","Arch"], tablefmt="simple_grid"))
            else:
                pt.fail("No valid sessions online found.")

            return

        elif args.K:
            c, st, sd = mt.exec_cmd(["adb", "disconnect"])
            if c == 0:
                pt.success("All sessions killed");return
            
            pt.fail("Failed to kill all adb sessions.")

        elif args.k:
            if args.k in devices:
                c, st, sd = mt.exec_cmd(["adb", "disconnect", args.k])
                if c == 0:
                    pt.success(f"Device '{args.k}' disconnected.");return
            
            pt.fail(f"Device '{args.k}' not found.")

        pt.error(f"Unknown instructions please use '{cl.RED}help sessions{cl.RESET}'")
        
    def do_sysinf(self, args):
        '''Show device specifications.'''
        self.session.sysinf()
        
    @cmd2.with_argparser(prs.send_key_parser)
    def do_send_key(self, args):
        if args.key:
            if args.key < 287 and args.key >= 0:
                self.session.send_key(str(args.key));return

        pt.error(f"Incorrect usage, use {cl.RED}help send_key{cl.RESET}.")
	
    @cmd2.with_argparser(prs.send_keys_parser)
    def do_send_keys(self, args):
        if args.keys:
            self.session.multikey(args.keys);return

        pt.error(f"Incorrect usage, use {cl.RED}help send_keys{cl.RESET}.")
    
    @cmd2.with_argparser(prs.send_text_parser)
    def do_send_text(self, args):
        if args.text:
            text = " ".join(args.text)
            self.session.send_text(text);return

        pt.error(f"Incorrect usage, use {cl.RED}help send_text{cl.RESET}.")
        
    @cmd2.with_argparser(prs.search_parser)
    def do_search(self, args):
        
        if args.term:
            self.session.search(term=args.term);return

        pt.error(f"Incorrect usage, use {cl.RED}help search{cl.RESET}.")
    
    @cmd2.with_argparser(prs.ripper_parser)
    def do_ripper(self, args):
        
        if args.l:
            self.session.ripper("list"); return
            
        elif args.r:
            _payload, _delay = args.r
            if mt.check_int(_delay):
                self.session.ripper(mode="run", payload=_payload, delay=int(_delay));return
            
            self.session.ripper(mode="run", payload=_payload);return

        pt.error(f"Incorrect usage, use {cl.RED}help ripper{cl.RESET}.")
        
    @cmd2.with_argparser(prs.clear_pkg_parser)
    def do_clear_pkg(self, args):
        if args.pkg:
            self.session.clear_package(args.pkg);return 
            
        pt.error(f"Incorrect usage, use {cl.RED}help clear_pkg{cl.RESET}.")
        
    @cmd2.with_argparser(prs.uninstall_parser)
    def do_uninstall(self, args):
        if args.pkg:
            self.session.uninstall(args.pkg);return 
            
        pt.error(f"Incorrect usage, use {cl.RED}help uninstall{cl.RESET}.")
        
    @cmd2.with_argparser(prs.install_parser)
    def do_install(self, args):
        if args.apk:
            self.session.install(args.apk);return
        
        pt.error(f"Incorrect usage, use {cl.RED}help install{cl.RESET}.")
        
    @cmd2.with_argparser(prs.list_pkgs_parser)
    def do_list_pkgs(self, args):
        
        if not args.term:
            self.session.list_packages();return
        elif args.term:
            self.session.list_packages(term=args.term);return
            
        pt.error(f"Incorrect usage, use {cl.RED}help list_pkgs{cl.RESET}.")
    
    @cmd2.with_argparser(prs.get_prop_parser)
    def do_get_prop(self, args):

        if not args.term:
            self.session.getprop();return
        elif args.term:
            self.session.getprop(term=args.term);return
        
        pt.error(f"Incorrect usage, use {cl.RED}help list_pkgs{cl.RESET}.")
        
    @cmd2.with_argparser(prs.start_app_parser)
    def do_start_app(self, args):
        if args.pkg:
            self.session.start_app(args.pkg);return
            
        pt.error(f"Incorrect usage, use {cl.RED}help start_app{cl.RESET}.")
        
    @cmd2.with_argparser(prs.send_parser)
    def do_send(self, args):
        if args.local_path and args.dest_path:
            self.session.send(args.local_path, args.dest_path);return
            
        pt.error(f"Incorrect usage, use {cl.RED}help send{cl.RESET}.")
        
    @cmd2.with_argparser(prs.dump_parser)
    def do_dump(self, args):
        if args.remote_path and args.local_path:
            self.session.dump(args.remote_path, args.local_path);return

        pt.error(f"Incorrect usage, use {cl.RED}help dump{cl.RESET}.")
        
    def do_raw_shell(self, args):
        '''Starts a raw shell in device.
usage: shell'''
        self.session.shell()
    
    @cmd2.with_argparser(prs.dump_sd_parser)
    def do_dump_sd(self, args):
        
        if args.e and "," not in args.e:
            _format = args.e
            _format = f".{_format.lstrip('.')}"
            self.session.dump_sd((_format,))
            return
            
        elif args.es:
            cleaned = []
            for item in args.es:
                item = item.strip().lower().lstrip(".")
                
                if not item or not item.isalnum():
                    continue
                
                cleaned.append(f".{item}")
        
            if not cleaned:
                pt.error("No valid extensions provided.");return
        
            self.session.dump_sd(tuple(cleaned))
            return

        pt.error(f"Incorrect usage, use {cl.RED}help dump_sd{cl.RESET}.")
        
    @cmd2.with_argparser(prs.input_spam_parser)
    def do_input_spam(self, args):
        if args.s:
            self.session.input_spam(mode="swipe-random");return
        
        elif args.t:
            self.session.input_spam(mode="tap-random");return
        
        elif args.k:
            self.session.input_spam(mode="keyevent-random");return
        
        elif args.p:
            self.session.input_spam(mode="press-spam");return
            
        pt.error(f"Incorrect usage, use {cl.RED}help input_spam{cl.RESET}.")
        
    def do_live(self, args):
        self.session.live()
        
    def do_dump_wpp(self, args):
        '''Try dump whatsapp data from device.
usage: dump_wpp'''
        self.session.dump_wpp()
        
    @cmd2.with_argparser(prs.screenrecord_parser)
    def do_screenrecord(self, args):
        if args.out:
            self.session.screenrecord(args.out);return
            
        pt.error(f"Incorrect usage, use {cl.RED}help screenrecord{cl.RESET}.")
        
    @cmd2.with_argparser(prs.screencap_parser)
    def do_screencap(self, args):
        if args.out:
            self.session.screencap(args.out);return
            
        pt.error(f"Incorrect usage, use {cl.RED}help screencap{cl.RESET}.")
        
if __name__ == "__main__":
    if mt.check_adb():
        AdbRipper(no_intro=True).cmdloop()

        


