#!/usr/bin/env bash

set -euo pipefail

HOSTS="/etc/hosts"
EHPC_HOSTS_INFO="/opt/qingcloud/ehpc-hosts.info"
BACKUP_DIR="/opt/qingcloud/backup"
HOSTS_BAK="${BACKUP_DIR}/hosts_`date -Iseconds`.bak"

mkdir -p ${BACKUP_DIR}
LINE_NO=`grep -n "metadata" ${HOSTS} | cut -d ":" -f 1`
cp ${HOSTS} ${HOSTS_BAK}
head -${LINE_NO} ${HOSTS_BAK} > ${HOSTS}
cat ${EHPC_HOSTS_INFO} >> ${HOSTS}
