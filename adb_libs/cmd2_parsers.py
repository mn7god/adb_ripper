import argparse
from .maintenance_utils import Maintenance as mt
from pathlib import Path

class Parsers:
	
	sessions_parser = argparse.ArgumentParser(description="ADB Sessions Manager.")
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
	
	sessions2_parser = argparse.ArgumentParser(description="ADB Sessions Manager.")
	group = sessions2_parser.add_mutually_exclusive_group()
	group.add_argument('-l', '--list', action="store_true", help="List all adb sessions alive.")
	group.add_argument('-K', '--kill-all', action="store_true", help="Kill all adb sessions alive.")
	group.add_argument('-k', '--kill', metavar=("ADB_SESSION"), help="Kill specified adb session.")
	
	send_key_parser = argparse.ArgumentParser(description="Send integer key events to device.")
	send_key_parser.add_argument('key', metavar=('KEY'), type=int, help="Key need to be an integer between 286 and 0")
	
	send_keys_parser = argparse.ArgumentParser(description="Send multiple integers key events to device.")
	send_keys_parser.add_argument('keys', nargs='+', metavar=('KEYS'), help="Every key in list need to be an integer between 286 and 0")
	
	send_text_parser = argparse.ArgumentParser(description="Send text event to input of device.")
	send_text_parser.add_argument('text', metavar=('TEXT'), nargs='+', help="Need to be string")
	
	search_parser = argparse.ArgumentParser(description="Search for files in device internal storage by term.")
	search_parser.add_argument('term', metavar=('TERM'), help="Need to be string")
	
	ripper_parser = argparse.ArgumentParser(description="Send text event to input of device.")
	ripper_group = ripper_parser.add_mutually_exclusive_group()
	ripper_group.add_argument('-l', '--list', action="store_true", help="List all available payloads.")
	ripper_group.add_argument('-r', '--run', metavar=("ADBP_NAME"), choices=mt.simple_list_adbp(), help="Run payload by name.")
	ripper_parser.add_argument('-d', '--delay', metavar=("DELAY"), type=float, help="Custom delay for payload execution.")
	
	clear_pkg_parser = argparse.ArgumentParser(description="Clear a package internal data.")
	clear_pkg_parser.add_argument('pkg', metavar=('PACKAGE'), help="Need to be a real package name.")
	
	start_app_parser = argparse.ArgumentParser(description="Start a package(app) in device.")
	start_app_parser.add_argument('pkg', metavar=('PACKAGE'), help="Need to be a real package name.")
	
	uninstall_parser = argparse.ArgumentParser(description="Uninstall a package from device.")
	uninstall_parser.add_argument('pkg', metavar=('PACKAGE'), help="Need to be a real package name.")
	
	install_parser = argparse.ArgumentParser(description="Install an apk in local path to device.")
	install_parser.add_argument('apk', metavar=('APK'), help="Need to be a real .apk path")
	
	list_pkgs_parser = argparse.ArgumentParser(description="List all packages found in device.")
	list_pkgs_parser.add_argument('term', nargs="?", metavar=("TERM"), help="Accepts a optional term to filter.")
	
	get_prop_parser = argparse.ArgumentParser(description="List all device properties.")
	get_prop_parser.add_argument('term', nargs="?", metavar=("TERM"), help="Accepts a optional term to filter.")
	
	send_parser = argparse.ArgumentParser(description="Sends a file from local path to the device.")
	send_parser.add_argument('local_path', metavar=('LOCAL_PATH'), type=str, help="Local file path to send.")
	send_parser.add_argument('remote_path', metavar=('REMOTE_PATH'), type=str, help="Remote path to send.")
	
	dump_parser = argparse.ArgumentParser(description="Dumps a file from remote path to a local path.")
	dump_parser.add_argument('remote_path', metavar=('REMOTE_PATH'),  type=str, help="Remote file to dump.")
	dump_parser.add_argument('local_path', metavar=('LOCAL_PATH'), type=str, help="Local path to receive file.")
	
	dump_sd_parser = argparse.ArgumentParser(description="Dumps a massive files from device internal storage.")
	dump_sd_group = dump_sd_parser.add_mutually_exclusive_group()
	dump_sd_group.add_argument('-e', '--extension', type=str, help="Searchs for a lot of files by extension.")
	dump_sd_group.add_argument('-es', '--extensions', nargs='+', help="Search for every extension in list format.")
		
	screenrecord_parser = argparse.ArgumentParser(description="Records the device screen.")
	screenrecord_parser.add_argument('out', metavar=('OUTPUT'), help="File name for screen record output.")
	
	screencap_parser = argparse.ArgumentParser(description="Takes a screenshot from device.")
	screencap_parser.add_argument('out', metavar=('OUTPUT'), help="File name for screenshot output.")
	
	force_stop_parser = argparse.ArgumentParser(description="Forces the termination of a package.")
	force_stop_parser.add_argument('pkg', metavar=('PACKAGE'), help="Package to stop.")
	
	open_url_parser = argparse.ArgumentParser(description="Open and URL in default device browser.")
	open_url_parser.add_argument('url', metavar=('URL'), help="Target URL.")
	
	send_msg_parser = argparse.ArgumentParser(description="Sends a message to device.")
	send_msg_parser.add_argument('msg', nargs='+', metavar=('MESSAGE'), type=str, help="Message to send.")
	
	spam_parser = argparse.ArgumentParser("Spam events to device.")
	spam_group = spam_parser.add_mutually_exclusive_group()
	spam_group.add_argument('-i','--input', choices=["swipe-random","tap-random","keyevent-random", "press-spam"], help="Send random input events.")
	spam_group.add_argument('-d','--display', choices=["brightness","battery","ui"], help="Send random screen events.")
	spam_group.add_argument('-m','--random-message', action="store_true", help="Send random messages to device.")
	spam_group.add_argument('-M','--message', nargs='+', help="Send repeatedly specified message.")
	spam_group.add_argument('-f','--force-stop', nargs='+', help="Force stop repeatedly in one or more packages.")
