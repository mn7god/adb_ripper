## DISCLAIMER:

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

## Introduction

ADB Ripper is a simple project focused almost 100% on getting the most out of the Android Debug Bridge. It’s written entirely in Python with very few external libraries and features a basic, slightly interactive CLI interface that makes it easy to use. It’s not a flawlessly organized project, but I guarantee it will be very useful for your purposes.

This project is also built exclusively for Linux; if you use Windows, you can use WSL (preferably Ubuntu or Debian).

## Lazy Setup

```bash
sudo apt -y install python3-venv;python3 -m venv venv;git clone https://github.com/mn7god/adb_ripper;cd adb_ripper; python3 -m venv venv;source venv/bin/activate; pip install -r requirements.txt
```

## Starting

```bash
python3 adb_ripper.py
```

## ADB Functions List:

### ♦ 



## PS:

Some commands may not work on very old versions of Android;
these include: list_notifications, send_msg, and send_msg_spam.

This script has been tested on Android versions 9, 13, and 16.
