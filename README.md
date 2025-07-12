# vt-automator
A small project that aims to automate pulling files off of the Vantrue N4 Pro dashcam

# Getting Started
What I have managed to do is gain telnet and ftp access to my Vantrue N4 Pro dashcam and successfully reconfigured it to act as a WPA supplicant (WiFi client) during parking mode. To do this yourself it will require some familiarity with a commandline. I am running NixOS (btw) and so any non-dashcam specific commands are likely to be the NixOS version, I'll make a note of this as we go through.

This project also assumes you have a battery for your dashcam that allows it to go into parking mode. While it is likely possible to have the dashcam turn on WiFi while driving this seems of little utility to me.

## Process Overview
1. Enable WiFi to be always on
2. CHANGE THE DEFAULT WIFI PASSWORD (seriously, do this)
3. Connect to the Dashcam's access point with a device capable of using telnet
4. telnet into the Dashcam (username root, no password)
5. CHANGE THE ROOT PASSWORD (using passwd)
6. Modify the /usr/share/wifiscripts/down.sh script
7. Modify the /etc/wpa_supplicant.conf script
8. Create a ftpuser
9. symlink /mnt/sd to the ftpuser's home directory
10. Done? The rest of this is all network side, not based on the dashcam

## Process Details
### 1. Enable WiFi
This is simply done using the Dashcam's buttons, navigate to System Settings > WiFi #TODO_menu_name and change the on/off/on for 10 minutes to be just on.

### 2. Changing default WiFi password
Do this in the Vantrue app

### 3 & 4. Connect to the Dashcam's AP then telnet in
I will be doing this with my laptop, for those on NixOS you need to add `pkgs.inetutils` to your packages or run a nix shell (`nix-shell -p inetutils`).
The dashcam will broadcast it's AP as soon as it powers on but will turn it off when it goes into parking mode (which happens after 10-15 minues). Restart the dashcam and wait for it's AP to become available, join the WiFi network and then attempt to telnet in:
`telnet 192.168.1.254`
It will as for a username, this should just be `root`, no password should be queried for. If all goes well you should be dropped into a shell.

### 5. Change the root password
Use command `passwd` and enter new password when prompted. It will complain about not having permissions to a file, I have found this doesn't actually affect changing the password.

### 6. Modify the down.sh script
Because I don't know how litigous Vantrue are, and there are no licence markers on the files I won't share the full files but I will share the script segments I have written which you can append yourself.
Navigate to /usr/share/wifiscripts/
`cd /usr/share/wifiscripts`
You can now use vi to edit the down.sh file. Append the contents of the down-append.sh file to down.sh ensuring that exit 0 is only present after the appended code and not before.
#### Why do this?
The `down.sh` file is called when the dashcam goes into parking mode to turn off the WiFi and therefore save power. Given this we can modify it wait till the AP is turned off and then reconfigure the WiFi interface to turn on as a WPA supplicant. In laymans terms, act like a normal WiFi devices and connect to a WiFi network. My script goes a bit further and will only keep the WiFi on if my home WiFi SSID is available and the dashcam can connect to it. This is so that the dashcam isn't keeping WiFi on during parking mode everywhere, only in my garage so I can pull footage from it.

### 7. Modify wpa_supplicant.conf
The `wpa_supplicant.conf` file defines what WiFi network we will be joining. The wpa_supplicant.conf file in this repo is the exact contents you require except replacing the CAPS statements with the correct info. If your WiFi is WPA Enterprise there is capability to support that but I won't delve into it here because, well, if you have WPA Enterprise you can likely figure it out :p. 

After you have done this you should be able to put the dashcam in parking mode and see it connect to your WiFi. If that happens you can complete the following steps over your LAN instead, this stops you being interrupted by the dashcam going into parking mode every 10-15 minutes and turning off the AP.

### 8. Create ftpuser
This step is technically optional, you could just use the root user for this but that gives me the ick. To add a user run the following commands:
`mkdir -p /home/ftpuser`
`adduser --home /home/ftpuser ftpuser`
`passwd ftpuser` - enter the password for `ftpuser` when prompted

### 9. Symlink
The ftp server will drop the user into their home directory by default, instead of changing that behaviour I've decided to create a symbolic link to the `/mnt/sd` directory which is where the footage is stored. To create the symlink
`cd /home/ftpuser`
`ln -s /mnt/sd`

### 10. Done?
I am still deciding how I will get the footage off the dashcam from a home server standpoint so this is as far as the guide (such as it is) will go. I hope to update this in future when I have a solution.
