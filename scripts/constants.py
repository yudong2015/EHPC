#!/usr/bin/env python


# appctl constants
HOSTS = "/etc/hosts"
WORK_DIR = "/opt/app"
APP_CONF_DIR = "{}/conf".format(WORK_DIR)
BACKUP_DIR = "{}/backup".format(WORK_DIR)
LOGGER_DIR = "{}/log".format(WORK_DIR)

HOSTS_INFO_FILE = "{}/hosts.info".format(APP_CONF_DIR)
RESOURCE_INFO_FILE = "{}/resource.info".format(APP_CONF_DIR)
CLUSTER_INFO_FILE = "{}/cluster.info".format(APP_CONF_DIR)

SLURM_CONF = "/etc/slurm/slurm.conf"
SLURM_CONF_TMPL = "{}/tmpl/slurm.conf.tmpl".format(WORK_DIR)

BACKUP_HOSTS_CMD = "cp {} {}/hosts_{}.bak".format(HOSTS, BACKUP_DIR, "{}")
BACKUP_SLURM_CONF_CMD = "cp {} {}/slurm.conf_{}.bak".format(SLURM_CONF, BACKUP_DIR, "{}")

ACTION_APP_INIT = "init"
ACTION_APP_START = "start"
ACTION_APP_STOP = "stop"
ACTION_APP_RESTART = "restart"
ACTION_HEALTH_CHECK = "check"

ROLE_CONTROLLER = "controller"
ROLE_COMPUTE = "compute"
ROLE_LOGIN = "login"

COMPUTE_HOSTNAME_PREFIX = "node"

# userctl constants
ACTION_USER_LIST = "list"
ACTION_USER_ADD = "add"
ACTION_USER_ADD_ADMIN = "add_admin"
ACTION_USER_DELETE = "delete"
ACTION_RESET_PASSWORD = "passwd"

ADMIN_HOME_FMT = "/home/{}"  # /home/nas_path
HOME_FMT = "/home/{}/home/{}"  # /home/nas_path/home/user_name

LDAP_ADDRESS = "ldap://controller:389"
LDAP_ROOT_DN = "dc=ehpccloud,dc=com"
LDAP_ADMIN = "ldapadm"
LDAP_ADMIN_PASSWORD = "Zhu1241jie"
