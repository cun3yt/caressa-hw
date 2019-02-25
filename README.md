[![Build Status](https://semaphoreci.com/api/v1/projects/90506832-0913-4cc8-8125-f32b1aacade5/2521956/badge.svg)](https://semaphoreci.com/caressa/caressa-hw)


# Caressa Hardware Initiation

## Setting a New Device From Scratch

To set a new device read INSTALLATION.md. 

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
* `pip install -r requirements/dev.txt`

## Development Ease

* ssh rsa key, ssh-add, etc. (https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md)
* In PyCharm: Tools > File Watcher to run `build.sh`.

## Todo

* Remote run from PyCharm for debugging...
* Security issue? What to do with credentials to be used by someone else with some other hardware? Location-based 
check? 

## Configuration

* Copy `config.template.json` as `config.json`.
* Fill these fields in `config.json`:
    * client ID and secret: Authentication server client ID and secret.
    * user's ID and hash: User credentials

## Caressa Main Process Unit/Service File

* `caressa.service` is a systemd unit file for make main process run whenever network is online.
* `.envservice` is a dependency for the `caressa.service` which is created remotely in the build file (`build.sh`).
* `caressa.service` file needs to be inside of a system directory with some permissions. 
For reference check `ls -l` output of a working version: 
`-rwxrwxrwx 1 root root 263 Nov 14 13:22 /etc/systemd/system/caressa.service` 
* Finally, run `systemctl enable caressa.service` for enable the service for once.

## Environment Variables

The following environment variables are in use. You can set `.envrc` file with these variable, which is used to generate `.envservice` by build scripts.

* ENV: Environment, e.g. 'dev', 'test', 'stage', 'prod'
* VIRTUAL_ENV_PATH: local directory path to virtual environment (e.g. /Users/cuneyt/Work/caressa_hw/venv/)
* Twilio Account Variables
    * TWILIO_ACCOUNT_SID
    * TWILIO_AUTH_TOKEN
* Pusher Account Variables
    * PUSHER_KEY_ID
    * PUSHER_SECRET
    * PUSHER_CLUSTER
* WEB_SUBDOMAIN: Domain of the Caressa API

## Development

* Install PyPi packages from requirements/dev.txt: `pip install -r requirements/dev.txt`
* Create `.envrc` with variables defined in "Environment Variables" section.
* Set `ENV` to `'dev'` in .envrc: `export ENV='dev'`
* Delete .git/hooks folder and symlink .git/hooks to scripts/githooks: `ln -s -f ./scripts/githooks/ .git/hooks`

## Running Tests

* Set `ENV` to `'test'` in .envrc: `export ENV='test'` 
* Install test requirements: `pip install -r requirements/test.txt`
* `coverage run -m unittest discover tests/ > /tmp/null`
* `coverage report`

## Patch for Fixing AIY Project

The first time the device is installed, the patch files `one-time/*.diff` must be applied. Dry-run them first:

```
cd ~/AIY-projects-python
patch src/aiy/audio.py --dry-run < ~/Work/one-time/aiy_audio.diff
patch src/aiy/_drivers/_recorder.py --dry-run < ~/Work/one-time/aiy_recorder.diff
``` 

Apply:

```
cd ~/AIY-projects-python
patch src/aiy/audio.py < ~/Work/one-time/aiy_audio.diff
patch src/aiy/_drivers/_recorder.py < ~/Work/one-time/aiy_recorder.diff
```

You'll need to restart the machine to make it available: `sudo shutdown now`.

* What is the downside of compromised client ID and client secret?