# DISCLAIMER:

This project heavily relies on ADB (Android Debug Bridge), a command-line tool distributed as part of the Android SDK by Google LLC.
This software is an independent, third-party project and is not affiliated with, endorsed by, sponsored by, or officially associated with Google LLC, Android, or the Android Open Source Project (AOSP).
ADB, Android, and all related names, logos, and trademarks are the property of their respective owners.
This project acts as a wrapper/interface that executes ADB commands. It does not modify, redistribute, or claim ownership of ADB itself.
This software is intended for development, testing, research, and educational purposes only. Improper use of ADB can lead to data loss, device malfunction, security vulnerabilities, or violation of local laws and service agreements.

By using this project, you acknowledge that:

You are responsible for complying with applicable laws and regulations.
You understand the risks of interacting with Android devices at a system level.
The author are not liable for any damage, data loss, security issues, account bans, warranty voiding, or other consequences resulting from the use or misuse of this software.

Use at your own risk.

# Introduction

ADB Ripper is a simple project focused almost 100% on getting the most out of the Android Debug Bridge. It’s written entirely in Python with very few external libraries and features a basic, slightly interactive CLI interface that makes it easy to use. It’s not a flawlessly organized project, but I guarantee it will be very useful for your purposes.

This project is also built exclusively for Linux; if you use Windows, you can use WSL (preferably Ubuntu or Debian).

# Lazy Setup

```bash
sudo apt -y install python3-venv;python3 -m venv venv;git clone https://github.com/mn7god/adb_ripper;cd adb_ripper; python3 -m venv venv;source venv/bin/activate; pip install -r requirements.txt
```

# Starting

```bash
python3 adb_ripper.py
```

# ADB Session Functions List:

➤ sessions - Basic adb sessions manager

➤ dump - Extracts any file from device storage 
➤ dump_permissions - Extracts all permissions from an app
➤ dump_sd - Extracts multiple files from device storage with extension filter
➤ dump_wpp - Extracts every type of media in whatsapp data path

➤ cmd - Executes any toybox cmd command
➤ force_stop - Stops any app process
➤ open_url - Opens any url in device browser
➤ ripper - Command focused on custom macros and payloads managing
➤ send_msg - Sends any notification with you custom text

➤ send_key - Sends one key event to device
➤ send_keys - Sends multiple sequential key events to device
➤ send_text - Sends any text to device

➤ battery - Command from adb to manage battery settings and stats
➤ display - Command from adb to manage display settings and stats
➤ clear_pkg - Clears internal data from any app on device
➤ get_host_cwd - Get current working directory from host(can be useful without cmd2 shell option)
➤ get_prop - Get propierties from device with string filter
➤ install - Install any android package(apk) you want on device
➤ uninstall - Uninstall any app you want on device
➤ list_pkgs - Lists all apps on device with string filters
➤ list_processes - Lists all processes on device with string filters
➤ live - Try improve a low complexity sharescreen with screenshots and html
➤ notifspy - Monitorates notification bar until the custom package appears in device and show current app on screen
➤ package_apk - Gets any app apk path of the device
➤ raw_shell - Opens a simple shell on device
➤ screencap - Takes an screenshot from device
➤ screenrecord - Starts an screenrecord of device
➤ search - Search any file or file type on the device
➤ send - Sends any file to device
➤ start_app - Starts any app by package name in device

# PS:

Some commands may not work on very old versions of Android;
these include: list_notifications, send_msg, and send_msg_spam.

This script has been tested on Android versions 9, 13, and 16.
