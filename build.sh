#!/usr/bin/env bash
HOST='rasp2'
USER='pi'
REMOTE_DIR='/home/pi/Work'
MAIN_CODE='main.py'

rsync -rvz --delete --exclude-from=.rsyncignore ~/Projects/caressa-hw/ "${USER}@${HOST}:${REMOTE_DIR}"


echo "RSync Done..."
echo "Running Script"

#ssh "${USER}@${HOST}" "python3 ${REMOTE_DIR}/${MAIN_CODE}"

#ssh pi@192.168.1.95 'cd ~/Work; source ~/virtual-environments/caressa1/bin/activate; pip install -r requirements.txt'

