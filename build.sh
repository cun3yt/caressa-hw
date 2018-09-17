#!/usr/bin/env bash
rsync -rvz --exclude-from=.rsyncignore ~/Work/caressa_hw/ pi@192.168.1.95:~/Work
#ssh pi@192.168.1.95 'cd ~/Work; source ~/virtual-environments/caressa1/bin/activate; pip install -r requirements.txt'
