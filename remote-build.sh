#!/usr/bin/env bash
HOST='localhost'
USER='pi'
REMOTE_DIR='/home/pi/Work'
ENV_FILE='.envrc'
ENV_SERVICE_FILE='.envservice'
SERVICE_UNIT_FILE='caressa.service'

if [[ $# -eq 0 ]]; then
    echo "Port numbers must be given as arguments"
    echo "Usage: remote-build.sh 9093 9091"
    exit 1
fi

FORWARD_PORTS=( "$@" )

for port in ${FORWARD_PORTS}; do
    echo "########   ######  ##    ## ##    ##  ######"
    echo "##     ## ##    ##  ##  ##  ###   ## ##    ##"
    echo "##     ## ##         ####   ####  ## ##"
    echo "########   ######     ##    ## ## ## ##"
    echo "##   ##         ##    ##    ##  #### ##"
    echo "##    ##  ##    ##    ##    ##   ### ##    ##"
    echo "##     ##  ######     ##    ##    ##  ######"
    echo ""
    echo "Port: ${port}"
    echo ""

    rsync -rvz -e "ssh -p ${port}" --delete --exclude-from=.rsyncignore ~/Work/caressa_hw/ "${USER}@${HOST}:${REMOTE_DIR}"

    echo ""
    echo "Generating Environment Variables for Service Unit: ${ENV_SERVICE_FILE}"
    echo ""

    ssh -p "${port}" "${USER}@${HOST}" "sed 's/^export\ //g' ${REMOTE_DIR}/${ENV_FILE} | sed '/^$/d' > ${REMOTE_DIR}/${ENV_SERVICE_FILE}"

    echo ""
    echo "Restarting Service: ${SERVICE_UNIT_FILE}"
    echo ""

    # sudo systemctl reload-or-restart caressa
    ssh -p "${port}" "${USER}@${HOST}" "sudo systemctl daemon-reload"
    ssh -p "${port}" "${USER}@${HOST}" "sudo systemctl restart ${SERVICE_UNIT_FILE}"
done

echo ""
echo "RSync to ${HOST} Done..."
