#!/usr/bin/python

from time import sleep
import requests
from settings import SUBDOMAIN
import os
import subprocess


URL = '{host}/version_check'.format(host=SUBDOMAIN)



while True:
    sleep(2)
    r = requests.get(url=URL)
    newest_version = r.json()
    file = open('/home/pi/Work/version.txt', 'r')
    current_version_ondevice = file.readline()
    file.close()
    process = subprocess.run("ps ax | pgrep -f pythin3 /home/Pi/Work/main.py",
                            shell=True,
                            stdout=subprocess.PIPE,
                            )
    main_process_pid = process.stdout.decode('UTF-8')
    print(newest_version + ' : version from caressa trio')
    print(current_version_ondevice + ' : current version of device')
    print(str(main_process_pid) + ' : main.py process info')
    if not newest_version == current_version_ondevice:
        file_to_write = open('/home/pi/Work/version.txt', 'w')
        os.system("echo Running Git Pull...")
        file_to_write.write(newest_version)
        file_to_write.close()
        os.system("kill -9 {}".format(main_process_pid))
        os.system("git pull git@github.com:cun3yt/caressa-hw.git")
    elif not main_process_pid:
        os.system("echo 'starting main.py, no changes'")
        os.system("source /home/pi/Work/.envrc")
        os.system("python3 /home/pi/Work/main.py")
    else:
        os.system("echo 'main.py running, no changes'")