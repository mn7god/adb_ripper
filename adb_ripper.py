import re
import sys
import cmd2
import argparse
from tabulate import tabulate
from adb_libs.printit import Color as cl
from adb_libs.printit import PrintIt as pt
from adb_libs.session_manager import SessionManager
from adb_libs.adb_session import AdbSession 
from adb_libs.cmd2_parsers import Parsers as prs
from adb_libs.maintenance_utils import Maintenance as mt

IP_RE = re.compile(r"^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$")
PORT_RE = re.compile(r"^(\d{4,5})$")
PAIR_CODE_RE = re.compile(r"^([0-9]{1}[0-9]{5})$")

class AdbRipper(cmd2.Cmd):
    
    def __init__(self, no_intro=False):
        super().__init__(
            persistent_history_file='.adb_history',
            persistent_history_length=100
        )
        self.no_intro = no_intro
        if self.no_intro:
            self.intro = ""
        else:
            self.intro = pt.banner()
            
        self.prompt = f"{cl.WHITE_LINE}adbr{cl.RESET}> "
        
    @cmd2.with_category("Connection manager")
    @cmd2.with_argparser(prs.sessions_parser)
    def do_sessions(self, args):
        devices = mt.check_devices()
        
        if args.list:
            s = mt.return_sessions()
            if s != {}:
                table = mt.sessions_formatter(s)
                print(tabulate(table, headers=["Device Name","System Kernel","Arch"], tablefmt="simple_grid"))
            else:
                pt.fail("No valid sessions online found.")

            return

        elif args.kill_all:
            c, st, sd = mt.exec_cmd(["adb", "disconnect"])
            if c == 0:
                pt.success("All sessions killed")
                return
            
            pt.fail("Failed to kill all adb sessions.")

        elif args.login:
            if args.login in devices:
                SessionManager(args.login).cmdloop()
                return
            
            pt.fail(f"Device '{args.login}' not found.")
            return

        elif args.kill:
            if args.kill in devices:
                c, st, sd = mt.exec_cmd(["adb", "disconnect", args.kill])
                if c == 0:
                    pt.success(f"Device '{args.k}' disconnected.")
                    return
                    
        elif args.connect:
            _ip, _port = args.connect
            if IP_RE.fullmatch(_ip) and PORT_RE.fullmatch(_port):
                c, st, sd = mt.exec_cmd(["adb", "connect", f"{_ip}:{_port}"])
                if c == 0 and not "failed to connect" in sd.lower():
                    pt.success(f"Connection successfull with device IP '{_ip}'.")
                    return
                
                pt.fail(f"Can't connect with device IP '{_ip}'.")
                return
                
        elif args.pair_connect:
            _ip, _ip_port, _pair_port, _pair_code = args.pair_connect
            condition = [
                IP_RE.fullmatch(_ip),
                PORT_RE.fullmatch(_ip_port),
                PORT_RE.fullmatch(_pair_port),
                PAIR_CODE_RE.fullmatch(_pair_code),
            ]
            if all(condition):
                c, st, sd = mt.exec_cmd(["adb", "pair", f"{_ip}:{_pair_port}", _pair_code])
                pair_block = {
                    c == 0,
                    "error" not in sd.lower(),
                    "failed" not in sd.lower()
                }
                if all(pair_block):
                    pt.success(f"Paired successfully with device IP '{_ip}'.")
                    c1, st1, sd1 = mt.exec_cmd(["adb", "connect", f"{_ip}:{_ip_port}"])
                    if c1 == 0 and not "failed" in sd.lower():
                        pt.success(f"Connected successfully with device IP '{_ip}'")
                        return
                    
                    pt.fail(f"Cant connect with device IP '{_ip}'.")
                    return
                
                pt.fail(f"Cant pair with device IP '{_ip}'.")
                return

        pt.incorrect_usage("sessions")
    
    @cmd2.with_category("Utils")
    def do_banner(self, arg):
        '''Displays a banner on the screen.'''
        pt.banner()
        
arg = argparse.ArgumentParser()
arg.add_argument('-q', '--quiet', action="store_true", help="Runs without banner display.")
args, unknown = arg.parse_known_args()

sys.argv = [sys.argv[0]] + unknown

if __name__ == "__main__":
    if mt.check_adb():
        if args.quiet:
            AdbRipper(no_intro=True).cmdloop()
        else:
            AdbRipper().cmdloop()
    else:
        pt.error("Please install android-tools.")
