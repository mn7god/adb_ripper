import re
import sys
import cmd2
import argparse
from tabulate import tabulate
from .printit import Color as cl
from .printit import PrintIt as pt
from .adb_session import AdbSession 
from .cmd2_parsers import Parsers as prs
from .maintenance_utils import Maintenance as mt

class SessionManager(cmd2.Cmd):
    
    def __init__(self, device: str):
        super().__init__(
            persistent_history_file='.session_history',
            persistent_history_length=1000
        )
        self.device = device
        if not self.device:
            raise ValueError("Need an specified device.")
        self.session = AdbSession(self.device)
        self.modules = {
            'auxiliary/list_open_ports': 
                [
                    "List tcp/udp ports in device", 
                    "normal", 
                    self.session.open_ports
                ],
            
            'auxiliary/list_saved_networks': 
                [
                    "List saved networks in device.", 
                    "normal", 
                    self.session.list_saved_networks
                ],
            
            'post/list_notifications': 
                [
                    "List device notifications.", 
                    "high", 
                    self.session.list_notifications
                ],
            
            'post/sysinf': 
                [
                    "Dump system informations.", 
                    "normal", 
                    self.session.sysinf
                ],
                
            'post/show_current_app': 
                [
                    "Shows screen current app package.", 
                    "medium", 
                    self.session.current_app
                ],
                
            'post/get_system_apks': 
                [
                    "List system default apks.", 
                    "medium", 
                    self.session.list_system_apks
                ],
                
            'post/get_user_apks': 
                [
                    "List users packages apks.", 
                    "medium", 
                    self.session.list_user_apks
                ]
        
        }
        self.formated_modules = mt.module_formater(self.modules)
        self.modules_table = tabulate(
            self.formated_modules,
            headers=["Module", "Description", "Rank"],
            tablefmt='simple_grid'
        )
        self.prompt = f"{cl.WHITE_LINE}session{cl.RESET}:{cl.RED}{self.device}{cl.RESET}> "
        mt.check_paths()
        
    @cmd2.with_category("Connection manager")
    @cmd2.with_argparser(prs.sessions2_parser)
    def do_sessions(self, args):
        
        devices = mt.check_devices()
        
        if args.list:
            s = mt.return_sessions()
            if s != {}:
                table = mt.sessions_formatter(s)
                print(
                    tabulate(
                        table, 
                        headers=["Device","System","Kernel Release"], 
                        tablefmt="simple_grid")
                    )
                return
            
            pt.fail("No valid sessions online found.")
            return

        elif args.kill_all:
            c, st, sd = mt.exec_cmd(["adb", "disconnect"])
            if c == 0:
                pt.success("All sessions killed")
                return
            
            pt.fail("Failed to kill all adb sessions.");
            return

        elif args.kill:
            if args.kill in devices:
                c, st, sd = mt.exec_cmd(["adb", "disconnect", args.kill])
                if c == 0:
                    pt.success(f"Device '{args.k}' disconnected.")
                    return
            
            pt.fail(f"Device '{args.k}' not found.")
            return
            
        pt.incorrect_usage("sessions")
    
    @cmd2.with_category("Input event")
    @cmd2.with_argparser(prs.send_key_parser)
    def do_send_key(self, args):
        if args.key:
            if args.key < 287 and args.key >= 0:
                self.session.send_key(str(args.key))
                return

        pt.incorrect_usage("send_key")
        
    @cmd2.with_category("Input event")
    @cmd2.with_argparser(prs.send_keys_parser)
    def do_send_keys(self, args):
        if args.keys:
            self.session.multikey(args.keys)
            return

        pt.incorrect_usage("send_keys")
    
    @cmd2.with_category("Input event")
    @cmd2.with_argparser(prs.send_text_parser)
    def do_send_text(self, args):
        if args.text:
            text = " ".join(args.text)
            self.session.send_text(text)
            return

        pt.incorrect_usage("send_text")
        
    @cmd2.with_category("Utils")
    @cmd2.with_argparser(prs.search_parser)
    def do_search(self, args):
        
        if args.term:
            self.session.search(term=args.term)
            return

        pt.incorrect_usage("search")
        
    @cmd2.with_category("Utils")
    @cmd2.with_argparser(prs.list_processes_parser)
    def do_list_processes(self, args):
        
        if not args.term:
            self.session.process_list()
            return
            
        elif args.term:
            self.session.process_list(args.term)
            return

        pt.incorrect_usage("search")
    
    @cmd2.with_category("Event executer")
    @cmd2.with_argparser(prs.ripper_parser)
    def do_ripper(self, args):
        
        if args.list_macros:
            self.session.ripper("list-macros")
            return
            
        elif args.run_macro and args.delay is not None:
            self.session.ripper(mode="run-macro", payload=args.run_macro, delay=args.delay)
            return
            
        elif args.run_macro:
            self.session.ripper(mode="run-macro", payload=args.run_macro)
            return
            
        elif args.list_modules:
            print(self.modules_table)
            return
            
        elif args.execute_module:
            self.modules[args.execute_module][2]()
            return
            
        pt.incorrect_usage("ripper")
        
    @cmd2.with_category("Utils")
    @cmd2.with_argparser(prs.clear_pkg_parser)
    def do_clear_pkg(self, args):
        if args.pkg:
            self.session.clear_package(args.pkg)
            return 
            
        pt.incorrect_usage("clear_pkg")
        
    @cmd2.with_category("Utils")
    @cmd2.with_argparser(prs.uninstall_parser)
    def do_uninstall(self, args):
        if args.pkg:
            self.session.uninstall(args.pkg)
            return 
            
        pt.incorrect_usage("uninstall")
        
    @cmd2.with_category("Utils")
    @cmd2.with_argparser(prs.install_parser)
    def do_install(self, args):
        if args.apk:
            self.session.install(args.apk)
            return
        
        pt.incorrect_usage("install")
        
    @cmd2.with_category("Utils")
    @cmd2.with_argparser(prs.list_pkgs_parser)
    def do_list_pkgs(self, args):
        
        if not args.term:
            self.session.list_packages()
            return
        
        elif args.term:
            self.session.list_packages(term=args.term)
            return
            
        pt.incorrect_usage("list_pkgs")
    
    @cmd2.with_category("Utils")
    @cmd2.with_argparser(prs.get_prop_parser)
    def do_get_prop(self, args):

        if not args.term:
            self.session.getprop()
            return
            
        elif args.term:
            self.session.getprop(term=args.term)
            return
        
        pt.incorrect_usage("get_prop")
        
    @cmd2.with_category("Utils")
    @cmd2.with_argparser(prs.start_app_parser)
    def do_start_app(self, args):
        if args.pkg:
            self.session.start_app(args.pkg)
            return
            
        pt.incorrect_usage("start_app")
        
    @cmd2.with_category("Utils")
    @cmd2.with_argparser(prs.package_apk_parser)
    def do_package_apk(self, args):
        if args.pkg:
            self.session.package_apk(args.pkg)
            return
            
        pt.incorrect_usage("package_apk")
        
    @cmd2.with_category("Utils")
    @cmd2.with_argparser(prs.send_parser)
    def do_send(self, args):
        if args.local_path and args.remote_path:
            self.session.send(args.local_path, args.remote_path);return
            
        pt.incorrect_usage("send")
        
    @cmd2.with_category("Dump")
    @cmd2.with_argparser(prs.dump_parser)
    def do_dump(self, args):
        if args.remote_path and args.local_path:
            self.session.dump(args.remote_path, args.local_path);return

        pt.incorrect_usage("dump")
        
    @cmd2.with_category("Dump")
    @cmd2.with_argparser(prs.dump_permissions_parser)
    def do_dump_permissions(self, args):
        if args.pkg:
            self.session.dump_permissions(args.pkg);return

        pt.incorrect_usage("dump")
    
    @cmd2.with_category("Utils")
    def do_raw_shell(self, args):
        '''Starts a raw shell in device.
usage: shell'''
        self.session.shell()
    
    @cmd2.with_category("Utils")
    def do_get_host_cwd(self, args):
        pt.success(f"Current dir: {mt.current_dir()}")
    
    @cmd2.with_category("Dump")
    @cmd2.with_argparser(prs.dump_sd_parser)
    def do_dump_sd(self, args):
        
        if args.extension and "," not in args.extension:
            _format = args.extension
            _format = f".{_format.lstrip('.')}"
            self.session.dump_sd((_format,))
            return
            
        elif args.extensions:
            cleaned = []
            for item in args.extensions:
                item = item.strip().lower().lstrip(".")
                
                if not item or not item.isalnum():
                    continue
                
                cleaned.append(f".{item}")
        
            if not cleaned:
                pt.error("No valid extensions provided.")
                return
        
            self.session.dump_sd(tuple(cleaned))
            return

        pt.incorrect_usage("dump_sd")
        
    @cmd2.with_category("Utils")
    def do_live(self, args):
        '''Starts a simulation of screenshare.'''
        self.session.live()
        
    @cmd2.with_category("Utils")
    @cmd2.with_argparser(prs.notif_spy_parser)
    def do_notifspy(self, args):
        if args.pkg:
            self.session.cli_notification_spy(args.pkg);return
            
        pt.incorrect_usage("notifspy")
        
    @cmd2.with_category("Dump")
    def do_dump_wpp(self, args):
        '''Try dump whatsapp data from device.
usage: dump_wpp'''
        self.session.dump_wpp()
        
    @cmd2.with_category("Utils")
    @cmd2.with_argparser(prs.screenrecord_parser)
    def do_screenrecord(self, args):
        if args.out:
            self.session.screenrecord(args.out);return
            
        pt.incorrect_usage("screenrecord")
        
    @cmd2.with_category("Utils")
    @cmd2.with_argparser(prs.screencap_parser)
    def do_screencap(self, args):
        if args.out:
            self.session.screencap(args.out);return
            
        pt.incorrect_usage("screencap")
        
    @cmd2.with_category("Event executer")
    @cmd2.with_argparser(prs.open_url_parser)
    def do_open_url(self, args):
        if args.url:
            self.session.open_url(args.url);return
            
        pt.incorrect_usage("open_url")
        
    @cmd2.with_category("Event executer")
    @cmd2.with_argparser(prs.force_stop_parser)
    def do_force_stop(self, args):
        if args.pkg:
            self.session.force_stop(args.pkg);return
            
        pt.incorrect_usage("force_stop")
        
    @cmd2.with_category("Event executer")
    def do_cmd(self, args):
        '''Control many events in device using 'cmd' command.
usage: cmd <FLAGS, SUB_COMMANDS>'''
        arg = args.split()
        if arg:
            self.session.cmd(arg);return
            
        pt.incorrect_usage("cmd")
        
    @cmd2.with_category("Utils")
    def do_battery(self, args):
        '''Manage battery stats.
usage: battery <FLAGS, SUB_COMMANDS>'''
        arg = args.split()
        if arg:
            self.session.battery(arg);return
            
        pt.incorrect_usage("battery")
        
    @cmd2.with_category("Utils")
    def do_display(self, args):
        '''Manage device display.
usage: display <FLAGS, SUB_COMMANDS>'''
        arg = args.split()
        if arg:
            self.session.display(arg);return
            
        pt.incorrect_usage("display")
    
    @cmd2.with_category("Event executer")
    @cmd2.with_argparser(prs.send_msg_parser)
    def do_send_msg(self, args):
        if args.msg:
            self.session.send_msg(" ".join(args.msg));return
            
        pt.incorrect_usage("send_msg")
    
    @cmd2.with_category("Event executer")
    @cmd2.with_argparser(prs.spam_parser)
    def do_spam(self, args):
        
        if args.input:
            self.session.spam(mode=args.input);return
            
        elif args.display:
            self.session.spam(mode=args.display);return
            
        elif args.random_message:
            self.session.spam(mode="send-msg");return
            
        elif args.message:
            self.session.spam(mode="send-msg", msg=" ".join(args.message));return
            
        elif args.force_stop:
            self.session.spam(mode="force-stop", pkgs=args.force_stop);return
        
        pt.incorrect_usage("spam")
