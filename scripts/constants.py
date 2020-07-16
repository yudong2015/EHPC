#!/usr/bin/env python


HOSTS = "/etc/hosts"
WORK_DIR = "/opt/app"
INFO_DIR = "{}/info".format(WORK_DIR)
BACKUP_DIR = "{}/backup".format(WORK_DIR)

HOSTS_INFO = "{}/hosts.info".format(INFO_DIR)
RESOURCE_INFO = "{}/resource.info".format(INFO_DIR)
CMP_SID_INFO = "{}/cmp-sid.info".format(INFO_DIR)
ROLE_INFO = "{}/role.info".format(INFO_DIR)
CLS_NAME_INFO = "{}/cluster-name.info".format(INFO_DIR)

SLURM_CONF = "/etc/slurm/slurm.conf"
SLURM_CONF_TMPL = "{}/slurm.conf.tmpl".format(WORK_DIR)

BACKUP_HOSTS_CMD = "cp {} {}/hosts_{}.bak".format(HOSTS, BACKUP_DIR, "{}")
BACKUP_SLURM_CONF_CMD = "cp {} {}/slurm.conf_{}.bak".format(SLURM_CONF, BACKUP_DIR, "{}")

ACTION_INIT = "init"
ACTION_START = "start"
ACTION_STOP = "stop"
ACTION_RESTART = "restart"

ROLE_CONTROLLER = "controller"
ROLE_COMPUTE = "compute"

START_CMDS = {
    ROLE_CONTROLLER: "systemctl start slurmctld",
    ROLE_COMPUTE: "systemctl start slurmd"
}
