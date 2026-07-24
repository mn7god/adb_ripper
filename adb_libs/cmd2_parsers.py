import cmd2
from .maintenance_utils import Maintenance as mt
from pathlib import Path

class Parsers:
	
	modules_list = sorted([
		"auxiliary/list_open_ports",
		"auxiliary/list_saved_networks",
		"post/show_current_app",
		"post/list_notifications",
		"post/sysinf",
		"post/sysprops",
		"post/get_system_apks",
		"post/get_user_apks"
	])
	
	sessions_parser = cmd2.Cmd2ArgumentParser(description="ADB Sessions Manager.")
	group = sessions_parser.add_mutually_exclusive_group()
	group.add_argument('-l', '--list', action="store_true", help="List all adb sessions alive.")
	group.add_argument('-K', '--kill-all', action="store_true", help="Kill all adb sessions alive.")
	group.add_argument('-k', '--kill', metavar=("ADB_SESSION"), help="Kill specified adb session.")
	group.add_argument('-L', '--login', metavar=("ADB_SESSION"), help="Login into a adb session.")
	group.add_argument('-c', '--connect', nargs=2, metavar=(
	        "DEVICE_IP",
	        "DEVICE_PORT"
	    ), help="Direct connection with adb device."
	)
	group.add_argument('-C', '--pair-connect', nargs=4, metavar=(
	        "DEVICE_IP", 
	        "DEVICE_PORT", 
	        "DEVICE_PAIR_PORT", 
	        "DEVICE_PAIR_CODE"
	    ), help="Pair and connect with adb device."
	    
	)
	
	sessions2_parser = cmd2.Cmd2ArgumentParser(description="ADB Sessions Manager.")
	group = sessions2_parser.add_mutually_exclusive_group()
	group.add_argument('-l', '--list', action="store_true", help="List all adb sessions alive.")
	group.add_argument('-K', '--kill-all', action="store_true", help="Kill all adb sessions alive.")
	group.add_argument('-k', '--kill', metavar=("ADB_SESSION"), help="Kill specified adb session.")
	
	send_key_parser = cmd2.Cmd2ArgumentParser(description="Send integer key events to device.")
	send_key_parser.add_argument('key', metavar=('KEY'), type=int, help="Key need to be an integer between 286 and 0")
	
	send_keys_parser = cmd2.Cmd2ArgumentParser(description="Send multiple integers key events to device.")
	send_keys_parser.add_argument('keys', nargs='+', metavar=('KEYS'), help="Every key in list need to be an integer between 286 and 0")
	
	send_text_parser = cmd2.Cmd2ArgumentParser(description="Send text event to input of device.")
	send_text_parser.add_argument('text', metavar=('TEXT'), nargs='+', help="Need to be string")
	
	search_parser = cmd2.Cmd2ArgumentParser(description="Search for files in device internal storage by term.")
	search_parser.add_argument('term', metavar=('TERM'), help="Need to be string")
	
	ripper_parser = cmd2.Cmd2ArgumentParser(description="Payloads and modules manager.")
	ripper_group = ripper_parser.add_mutually_exclusive_group()
	ripper_group.add_argument('-l', '--list-macros', action="store_true", help="List all available macro payloads.")
	ripper_group.add_argument('-r', '--run-macro', metavar=("ADBP_NAME"), help="Run macro payload by name.")
	ripper_group.add_argument('-e', '--execute-module', metavar=("MODULE_NAME"), choices=modules_list, help="Run module by name.")
	ripper_group.add_argument('-lm', '--list-modules', action='store_true', help="List all modules available.")
	ripper_parser.add_argument('-d', '--delay', metavar=("DELAY"), type=float, help="Custom delay for macro payload execution.")
	
	clear_pkg_parser = cmd2.Cmd2ArgumentParser(description="Clear a package internal data.")
	clear_pkg_parser.add_argument('pkg', metavar=('PACKAGE'), help="Need to be a real package name.")
	
	start_app_parser = cmd2.Cmd2ArgumentParser(description="Start a package(app) in device.")
	start_app_parser.add_argument('pkg', metavar=('PACKAGE'), help="Need to be a real package name.")
	
	package_apk_parser = cmd2.Cmd2ArgumentParser(description="Start a package(app) in device.")
	package_apk_parser.add_argument('pkg', metavar=('PACKAGE'), help="Need to be a real package name.")
	
	uninstall_parser = cmd2.Cmd2ArgumentParser(description="Uninstall a package from device.")
	uninstall_parser.add_argument('pkg', metavar=('PACKAGE'), help="Need to be a real package name.")
	
	install_parser = cmd2.Cmd2ArgumentParser(description="Install an apk in local path to device.")
	install_parser.add_argument('apk', metavar=('APK'), help="Need to be a real .apk path")
	
	list_pkgs_parser = cmd2.Cmd2ArgumentParser(description="List all packages found in device.")
	list_pkgs_parser.add_argument('term', nargs="?", metavar=("TERM"), help="Accepts a optional term to filter.")
	
	get_prop_parser = cmd2.Cmd2ArgumentParser(description="List all device properties.")
	get_prop_parser.add_argument('term', nargs="?", metavar=("TERM"), help="Accepts a optional term to filter.")
	
	list_processes_parser = cmd2.Cmd2ArgumentParser(description="List all device properties.")
	list_processes_parser.add_argument('term', nargs="?", metavar=("TERM"), help="Accepts a optional term to filter.")
	
	send_parser = cmd2.Cmd2ArgumentParser(description="Sends a file from local path to the device.")
	send_parser.add_argument('local_path', metavar=('LOCAL_PATH'), type=str, help="Local file path to send.")
	send_parser.add_argument('remote_path', metavar=('REMOTE_PATH'), type=str, help="Remote path to send.")
	
	dump_parser = cmd2.Cmd2ArgumentParser(description="Dumps a file from remote path to a local path.")
	dump_parser.add_argument('remote_path', metavar=('REMOTE_PATH'),  type=str, help="Remote file to dump.")
	dump_parser.add_argument('local_path', metavar=('LOCAL_PATH'), type=str, help="Local path to receive file.")
	
	dump_sd_parser = cmd2.Cmd2ArgumentParser(description="Dumps a massive files from device internal storage.")
	dump_sd_group = dump_sd_parser.add_mutually_exclusive_group()
	dump_sd_group.add_argument('-e', '--extension', type=str, help="Searchs for a lot of files by extension.")
	dump_sd_group.add_argument('-es', '--extensions', nargs='+', help="Search for every extension in list format.")
		
	screenrecord_parser = cmd2.Cmd2ArgumentParser(description="Records the device screen.")
	screenrecord_parser.add_argument('out', metavar=('OUTPUT'), help="File name for screen record output.")
	
	screencap_parser = cmd2.Cmd2ArgumentParser(description="Takes a screenshot from device.")
	screencap_parser.add_argument('out', metavar=('OUTPUT'), help="File name for screenshot output.")
	
	force_stop_parser = cmd2.Cmd2ArgumentParser(description="Forces the termination of a package.")
	force_stop_parser.add_argument('pkg', metavar=('PACKAGE'), help="Package to stop.")
	
	notif_spy_parser = cmd2.Cmd2ArgumentParser(description="Spy a package notifications.")
	notif_spy_parser.add_argument('pkg', metavar=('PACKAGE'), help="Package to spy.")
	
	dump_permissions_parser = cmd2.Cmd2ArgumentParser(description="Dump all package permissions.")
	dump_permissions_parser.add_argument('pkg', metavar=('PACKAGE'), help="Package to dump.")
	
	open_url_parser = cmd2.Cmd2ArgumentParser(description="Open and URL in default device browser.")
	open_url_parser.add_argument('url', metavar=('URL'), help="Target URL.")
	
	send_msg_parser = cmd2.Cmd2ArgumentParser(description="Sends a message to device.")
	send_msg_parser.add_argument('msg', nargs='+', metavar=('MESSAGE'), type=str, help="Message to send.")
	
	spam_parser = cmd2.Cmd2ArgumentParser("Spam events to device.")
	spam_group = spam_parser.add_mutually_exclusive_group()
	spam_group.add_argument('-i','--input', choices=["swipe-random","tap-random","keyevent-random", "press-spam"], help="Send random input events.")
	spam_group.add_argument('-d','--display', choices=["brightness","battery","ui"], help="Send random screen events.")
	spam_group.add_argument('-m','--random-message', action="store_true", help="Send random messages to device.")
	spam_group.add_argument('-M','--message', nargs='+', help="Send repeatedly specified message.")
	spam_group.add_argument('-f','--force-stop', nargs='+', help="Force stop repeatedly in one or more packages.")
	
