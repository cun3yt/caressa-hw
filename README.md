# Caressa Hardware Initiation

## Requirements

* Python 3.5.3
* ssh rsa key, ssh-add, etc.
* Update `build.sh` accordingly
* `pyvenv ~/virtual-environments/caressa1`
* install rpi.gpio: `sudo apt-get install rpi.gpio` (USE PIP PACKAGE INSTEAD, it is included in the requirements file)
* run daemon: `sudo pigpiod` (activate on startup...)

### omx-player-wrapper
* `sudo apt-get update` 
* `sudo apt-get install -y libdbus-1-3`
* `sudo apt-get install -y libdbus-1-dev`
* python-dbus-dev
* python-dbus
* dbus
* `omxplayer-wrapper`

## Todo

* Remote run from PyCharm for debugging...


