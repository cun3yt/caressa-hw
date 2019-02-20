#!/usr/bin/env bash
HOST='localhost'
USER='pi'
REMOTE_DIR='/home/pi/Work'
ENV_FILE='.envrc'
ENV_SERVICE_FILE='.envservice'
FORWARD_PORTS=(9091)    # todo take from command line

for port in $FORWARD_PORTS; do
    echo "RSync'ing to port ${port}"
    rsync -rvz -e "ssh -p ${port}" --delete --exclude-from=.rsyncignore ~/Work/caressa_hw/ "${USER}@${HOST}:${REMOTE_DIR}"
    ssh -p "${port}" "${USER}@${HOST}" "sed 's/^export\ //g' ${REMOTE_DIR}/${ENV_FILE} | sed '/^$/d' > ${REMOTE_DIR}/${ENV_SERVICE_FILE}"
    ssh -p "${port}" "${USER}@${HOST}" "sudo systemctl restart caressa.service"
done

echo "RSync to ${HOST} Done..."
echo "Running Script"

# Environment file for the service in Raspberry Pi is different than the original environment file `.envrc`,
# so generating the service env file with the removal of "export " at the beginning of each line of
# the original environment file:
