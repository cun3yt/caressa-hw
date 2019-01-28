#!/usr/bin/env bash
HOST='rasp'
USER='pi'
REMOTE_DIR='/home/pi/Work'
ENV_FILE='.envrc'
ENV_SERVICE_FILE='.envservice'

rsync -rvz --delete --exclude-from=.rsyncignore ~/Work/caressa_hw/ "${USER}@${HOST}:${REMOTE_DIR}"

echo "RSync Done..."
echo "Running Script"

# Environment file for the service in Raspberry Pi is different than the original environment file `.envrc`,
# so generating the service env file with the removal of "export " at the beginning of each line of
# the original environment file:

#ssh "${USER}@${HOST}" "sed 's/^export\ //g' ${REMOTE_DIR}/${ENV_FILE} | sed '/^$/d' > ${REMOTE_DIR}/${ENV_SERVICE_FILE}"
#ssh "${USER}@${HOST}" "sudo systemctl restart caressa.service"
