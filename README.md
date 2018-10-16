# Caressa Hardware Initiation

## Google AIY Set

* Aptitude
    * vlc
* Python3
    * python-vlc
    * gpiozero==1.4.1
* ~/.ssh/config:
```
Host rasp
        HostName 192.168.1.90
        UseKeychain yes
        AddKeysToAgent yes
        IdentityFile ~/.ssh/raspberry_rsa
```

## Env Variables

There are environment variables. All are supposed to be in `settings.py`.

## For 

* `sudo apt-get install libgtk-3-dev`
* `sudo apt-get install python3-gi`

## On Mac:

(based on this: https://apple.stackexchange.com/questions/169601/no-package-libffi-found-in-homebrew-virtual-environment)
* In order to install the pygobject3 it requires the PKG_CONFIG_PATH varibale for `libffi`: 
`export PKG_CONFIG_PATH=/usr/local/Cellar/libffi/3.2.1/lib/pkgconfig/`
* `brew install pygobject3`

## Development Ease

* ssh rsa key, ssh-add, etc. (https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md)
* In PyCharm: Tools > File Watcher to run `build.sh`.

## Todo

* Remote run from PyCharm for debugging...
