#!/usr/bin/env bash

set -euo pipefail

ACTION=$1

function init(){
  # TODO: generate slurm conf for login_node
  ./generate_hosts.sh
  ./generate_slurm_conf.sh
}

function start(){
  role=`curl http://metadata/self/host/role`
  if [[ "${role}" -eq "controller" ]]; then
    systemctl start slurmctld
  elif [[ "${role}" -eq "compute" ]]; then
    systemctl start slurmctld
  else
    echo "The starting service of role[${role}] not exist!"
    exit 1
  fi
}

function start(){
  role=`curl http://metadata/self/host/role`
  if [[ "${role}" -eq "controller" ]]; then
    systemctl start slurmctld
  elif [[ "${role}" -eq "compute" ]]; then
    systemctl start slurmctld
  else
    echo "The starting service of role[${role}] not exist!"
    exit 1
  fi
}



if [[ "${ACTION}" -eq "init" ]]; then
  init
elif [[ "${ACTION}" -eq "start" ]]; then


fi