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

(based on this: http://bit.ly/2St8qiT)
* In order to install the pygobject3 it requires the PKG_CONFIG_PATH varibale for `libffi`: 
`export PKG_CONFIG_PATH=/usr/local/Cellar/libffi/3.2.1/lib/pkgconfig/`
* `brew install pygobject3`

## Development Ease

* ssh rsa key, ssh-add, etc. (https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md)
* In PyCharm: Tools > File Watcher to run `build.sh`.

## Todo

* Remote run from PyCharm for debugging...

## Caressa Main Process Unit/Service File

* `caressa.service` is a systemd unit file for make main process run whenever network is online.
* `.envservice` is a dependency for the `caressa.service` which is created remotely in the build file (`build.sh`).
* `caressa.service` file needs to be inside of a system directory with some permissions. 
For reference check `ls -l` output of a working version: 
`-rwxrwxrwx 1 root root 263 Nov 14 13:22 /etc/systemd/system/caressa.service` 
* Finally, run `systemctl enable caressa.service` for enable the service for once.

## Patch for Fixing AIY Project

For the first time the device is installed the patch file `one-time/aiy.diff` must be applied. Dry-run first:

```
cd ~/AIY-projects-python
patch --dry-run < ~/Work/one-time/aiy.diff
``` 

Apply:

```
cd ~/AIY-projects-python
patch < ~/Work/one-time/aiy.diff
```
