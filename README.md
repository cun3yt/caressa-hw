# Caressa Hardware Initiation

## Requirements

* Python 3.5.3
* ssh rsa key, ssh-add, etc.
* Update `build.sh` accordingly
* `pyvenv ~/virtual-environments/caressa1`
* install rpi.gpio: `sudo apt-get install rpi.gpio` (USE PIP PACKAGE INSTEAD, it is included in the requirements file)
* run daemon: `sudo pigpiod` (activate on startup...)
