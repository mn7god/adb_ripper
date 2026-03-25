import argparse
from .maintenance_utils import Maintenance as mt

class Parsers:
	
	sessions_parser = argparse.ArgumentParser(description="ADB Sessions Manager.")
	group = sessions_parser.add_mutually_exclusive_group()
	group.add_argument('-l', action="store_true", help="List all adb sessions alive.")
	group.add_argument('-K', action="store_true", help="Kill all adb sessions alive.")
	group.add_argument('-k', metavar=(
	        "ADB_SESSION"
	    ), help="Kill specified adb session.", 
	)
	group.add_argument('-L', metavar=(
	        "ADB_SESSION"
	    ), help="Login into a adb session."
	)
	group.add_argument('-c', nargs=2, metavar=(
	        "DEVICE_IP",
	        "DEVICE_PORT"
	    ), help="Direct connection with adb device."
	)
	group.add_argument('-C', nargs=4, metavar=(
	        "DEVICE_IP", 
	        "DEVICE_PORT", 
	        "DEVICE_PAIR_PORT", 
	        "DEVICE_PAIR_CODE"
	    ), help="Pair and connect with adb device."
	    
	)
	
	sessions2_parser = argparse.ArgumentParser(description="ADB Sessions Manager.")
	group = sessions2_parser.add_mutually_exclusive_group()
	group.add_argument('-l', action="store_true", help="List all adb sessions alive.")
	group.add_argument('-K', action="store_true", help="Kill all adb sessions alive.")
	group.add_argument('-k', metavar=(
	        "ADB_SESSION"
	    ), help="Kill specified adb session."
	)
	
	send_key_parser = argparse.ArgumentParser(description="Send integer key events to device.")
	send_key_parser.add_argument('key', type=int, help="Key need to be an integer between 286 and 0")
	
	send_keys_parser = argparse.ArgumentParser(description="Send multiple integers key events to device.")
	send_keys_parser.add_argument('keys', nargs='+', help="Every key in list need to be an integer between 286 and 0")
	
	send_text_parser = argparse.ArgumentParser(description="Send text event to input of device.")
	send_text_parser.add_argument('text', nargs='+', help="Need to be string")
	
	search_parser = argparse.ArgumentParser(description="Search for files in device internal storage by term.")
	search_parser.add_argument('term', help="Need to be string")
	
	ripper_parser = argparse.ArgumentParser(description="Send text event to input of device.")
	ripper_group = ripper_parser.add_mutually_exclusive_group()
	ripper_group.add_argument('-l', action="store_true", help="List all available payloads.")
	ripper_group.add_argument('-r', nargs=2, metavar=("ADBP_NAME", "DELAY"), help="Run payload by name and accepts custom delay.")
	
	clear_pkg_parser = argparse.ArgumentParser(description="Clear a package internal data.")
	clear_pkg_parser.add_argument('pkg', help="Need to be a real package name.")
	
	start_app_parser = argparse.ArgumentParser(description="Start a package(app) in device.")
	start_app_parser.add_argument('pkg', help="Need to be a real package name.")
	
	uninstall_parser = argparse.ArgumentParser(description="Uninstall a package from device.")
	uninstall_parser.add_argument('pkg', help="Need to be a real package name.")
	
	install_parser = argparse.ArgumentParser(description="Install an apk in local path to device.")
	install_parser.add_argument('apk', help="Need to be a real .apk path")
	
	list_pkgs_parser = argparse.ArgumentParser(description="List all packages found in device.")
	list_pkgs_parser.add_argument('term', nargs="?", metavar=("TERM"), help="Accepts a optional term to filter.")
	
	input_spam_parser = argparse.ArgumentParser("Spam random or fixed key events until users stops.")
	input_spam_group = input_spam_parser.add_mutually_exclusive_group()
	input_spam_group.add_argument("-s", action="store_true", help="Sends random swipes coordinates to device.")
	input_spam_group.add_argument("-t", action="store_true", help="Sends random taps coordinates to device.")
	input_spam_group.add_argument("-k", action="store_true", help="Sends random key event codes to device.")
	input_spam_group.add_argument("-p", action="store_true", help="Sends press event to device.")
	
	get_prop_parser = argparse.ArgumentParser(description="List all device properties.")
	get_prop_parser.add_argument('term', nargs="?", metavar=("TERM"), help="Accepts a optional term to filter.")
	
	send_parser = argparse.ArgumentParser(description="Sends a file from local path to the device.")
	send_parser.add_argument('local_path', type=str, help="Local file path to send.")
	send_parser.add_argument('dest_path', type=str, help="Remote path to send.")
	
	dump_parser = argparse.ArgumentParser(description="Dumps a file from remote path to a local path.")
	dump_parser.add_argument('remote_path', type=str, help="Remote file to dump.")
	dump_parser.add_argument('local_path', type=str, help="Local path to receive file.")
	
	dump_sd_parser = argparse.ArgumentParser(description="Dumps a massive files from device internal storage.")
	dump_sd_group = dump_sd_parser.add_mutually_exclusive_group()
	dump_sd_group.add_argument('-e', type=str, help="Searchs for a lot of files by extension.")
	dump_sd_group.add_argument('-es', nargs='+', help="Search for every extension in list format.")
		
	screenrecord_parser = argparse.ArgumentParser(description="Records the device screen.")
	screenrecord_parser.add_argument('out', help="File name for screen record output.")
	
	screencap_parser = argparse.ArgumentParser(description="Takes a screenshot from device.")
	screencap_parser.add_argument('out', help="File name for screenshot output.")
	
	
