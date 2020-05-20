#!/usr/bin/env bash

set -euo pipefail

RESOURCE_INFO="/opt/qingcloud/resource.info"
CMP_SID_INFO="/opt/qingcloud/cmp-sid.info"
SLURM_CONF="/etc/slurm/slurm.conf"
SLURM_CONF_TMP="/opt/qingcloud/slurm.conf.tmpl"
BACKUP_DIR="/opt/qingcloud/backup"
mkdir -p ${BACKUP_DIR}


CLS_NAME=`curl http://metadata/self/env/cluster_name`
if [[ "${CLS_NAME}" == "Not found" ]]; then
  echo "The cluster name not found from metadata!"
  exit 1
fi
CTL_RESOURCE=`head -n 1 ${RESOURCE_INFO}`
CMP_RESOURCE=`tail -n 1 ${RESOURCE_INFO}`


# generate default NodeName, eg: node[1-6,8,12-15]
SIDS=`sort -n ${CMP_SID_INFO}`
echo "sids: ${SIDS}"
RANGE=""  # 1-6
RANGE_START=0 # 1
LAST_SID=0

NAME_NO="["  # [1-6,8]
for sid in ${SIDS}
do
  if [[ -n "${sid}" ]]; then
    if [[ -n "${RANGE}" ]]; then
      if [[ $[$sid - $LAST_SID] > 1 ]]; then

        if [[ "${RANGE_START}" -ne "${LAST_SID}" ]]; then
          RANGE="${RANGE}-${LAST_SID}"
        fi
        NAME_NO="${NAME_NO}${RANGE}"
        RANGE_START=${sid}
        RANGE=",${}"
      fi
    else
      RANGE_START=${sid}
      if [[ -n "${NAME_NO}" ]]; then
        RANGE=",${RANGE_START}"
      else
        RANGE="[${RANGE_START}"
      fi
    fi
    LAST_SID=${sid}
  fi
done
NAME_NO="${NAME_NO}]"


# backup last slurm configuration
BACKUP_FILE="${BACKUP_DIR}/slurm.conf_`date -Iseconds`.bak"
cp ${SLURM_CONF} ${BACKUP_FILE}


sed -e "s/{{CLUSTER_NAME}}/${CLS_NAME}/g" \
    -e "s/{{CONTROLLER_RESOURCE}}/${CTL_RESOURCE}/g" \
    -e "s/{{COMPUTE_RESOURCE}}/${CMP_RESOURCE}/g" \
    -e "s/{{DEFAULT_NODE_NAME}}/${NAME_NO}/g" \
 ${SLURM_CONF_TMP} > ${SLURM_CONF}
