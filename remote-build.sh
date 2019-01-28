#!/usr/bin/env bash
HOST='localhost'
USER='pi'
REMOTE_DIR='/home/pi/Work'
MAIN_CODE='main_aiy.py'
ENV_FILE='.envrc'
ENV_SERVICE_FILE='.envservice'
FORWARD_PORTS=(9192)

#rsync -rvz --delete --exclude-from=.rsyncignore ~/Work/caressa_hw/ "${USER}@${HOST}:${REMOTE_DIR}"

for port in $FORWARD_PORTS; do
    echo "RSync'ing to port ${port}"
    rsync -rvz -e "ssh -p ${port}" --delete --exclude-from=.rsyncignore ~/Work/caressa_hw/ "${USER}@${HOST}:${REMOTE_DIR}"
done

echo "RSync to ${HOST} Done..."
echo "Running Script"

# Environment file for the service in Raspberry Pi is different than the original environment file `.envrc`,
# so generating the service env file with the removal of "export " at the beginning of each line of
# the original environment file:

#ssh "${USER}@${HOST}" "sed 's/^export\ //g' ${REMOTE_DIR}/${ENV_FILE} | sed '/^$/d' > ${REMOTE_DIR}/${ENV_SERVICE_FILE}"
#ssh "${USER}@${HOST}" "sudo systemctl restart caressa.service"



#ssh "${USER}@${HOST}" "python3 ${REMOTE_DIR}/${MAIN_CODE}"
#ssh pi@192.168.1.95 'cd ~/Work; source ~/virtual-environments/caressa1/bin/activate; pip install -r requirements.txt'
