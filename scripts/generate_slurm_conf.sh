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
SIDS=`sort -nu ${CMP_SID_INFO} | grep -v "^$"`
SIDS=(${SIDS//\n/})
echo "sids: ${SIDS[@]}"
NODE_NAME="node["  # eg: [1-6,8]
RANGE_START=${SIDS[0]}
LAST_SID=${RANGE_START}

for sid in ${SIDS[@]}
do
  if [[ $[$sid - $LAST_SID] > 1 ]]; then
    if [[ ${LAST_SID} -ne ${RANGE_START} ]]; then
      NODE_NAME="${NODE_NAME}${RANGE_START}-${LAST_SID},"
    else
      NODE_NAME="${NODE_NAME}${RANGE_START},"
    fi
    RANGE_START=${sid}
  fi
  LAST_SID=${sid}
done

if [[ ${LAST_SID} -ne ${RANGE_START} ]]; then
  NODE_NAME="${NODE_NAME}${RANGE_START}-${LAST_SID}]"
else
  NODE_NAME="${NODE_NAME}${RANGE_START}]"
fi


# backup last slurm configuration
BACKUP_FILE="${BACKUP_DIR}/slurm.conf_`date -Iseconds`.bak"
cp ${SLURM_CONF} ${BACKUP_FILE}


# replace slurm.conf.teamplate
sed -e "s/{{CLUSTER_NAME}}/${CLS_NAME}/g" \
    -e "s/{{CONTROLLER_RESOURCE}}/${CTL_RESOURCE}/g" \
    -e "s/{{COMPUTE_RESOURCE}}/${CMP_RESOURCE}/g" \
    -e "s/{{DEFAULT_NODE_NAME}}/${NODE_NAME}/g" \
 ${SLURM_CONF_TMP} > ${SLURM_CONF}
