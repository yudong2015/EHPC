#!/usr/bin/env python

import sys
from os import path
from constants import (
    ACTION_APP_INIT,
    ACTION_APP_START,
    ACTION_APP_STOP,
    ACTION_APP_RESTART,
    ACTION_HEALTH_CHECK,
    ACTION_USER_ADD_ADMIN,
    ROLE_CONTROLLER,
    ROLE_COMPUTE,
    ROLE_LOGIN,
)
from common import (
    logger,
    run_shell,
    get_role,
)
from host_utils import generate_hosts, set_hostname
from slurm_utils import generate_conf

ROLE_SERVICES = {
    ROLE_CONTROLLER: ["slurmctld", "slapd"],
    ROLE_COMPUTE: ["slurmd", "nslcd"],
    ROLE_LOGIN: ["nslcd"],
}


def setup():
    logger.info("Generating hosts...")
    generate_hosts()

    logger.info("Create log home...")
    run_shell("mkdir -p /opt/app/log")

    logger.info("Setup hostname...")
    set_hostname()

    logger.info("Generating hosts for slurm configurations...")
    generate_conf()
    logger.info("setup done.")


def start():
    role = get_role()
    if role in ROLE_SERVICES:
        for service in ROLE_SERVICES[role]:
            run_shell("systemctl start {}".format(service))
    else:
        logger.error("Un-support role[%s].", role)
        sys.exit(1)

    if role == ROLE_CONTROLLER:
        # create admin user
        run_shell("userctl {}".format(ACTION_USER_ADD_ADMIN))
    else:
        userctl_file = "/usr/sbin/userctl"
        if path.exists(userctl_file):
            run_shell("rm {}".format(userctl_file))
    logger.info("%s started.", role)


def stop():
    role = get_role()
    if role in ROLE_SERVICES:
        for service in ROLE_SERVICES[role]:
            run_shell("systemctl stop {}".format(service))
    else:
        logger.error("Un-support role[%s].", role)
        sys.exit(1)


def restart():
    role = get_role()
    if role in ROLE_SERVICES:
        for service in ROLE_SERVICES[role]:
            run_shell("systemctl restart {}".format(service))
    else:
        logger.error("Un-support role[%s].", role)
        sys.exit(1)
    logger.info("%s re-started.", role)


def check_service_status(service):
    retcode = run_shell("systemctl is-active {}".format(service), without_log=True)
    if retcode != 0:
        logger.error("the {} service is not health.".format(service))
        sys.exit(retcode)
    return retcode


def health_check():
    role = get_role()
    services = ROLE_SERVICES.get(role, "")
    for service in services:
        check_service_status(service)
    sys.exit(0)


def help():
    logger.info("usage: appctl init/start/stop")


ACTION_MAP = {
    ACTION_APP_INIT: setup,
    ACTION_APP_START: start,
    ACTION_APP_STOP: stop,
    ACTION_APP_RESTART: restart,
    ACTION_HEALTH_CHECK: health_check,
}


def main(argv):
    if len(argv) < 2:
        help()
        sys.exit(1)
    else:
        action = argv[1]

    if action in ACTION_MAP:
        ACTION_MAP[action]()
    else:
        logger.error("Un-support action:[%s], exist!", action)
        help()
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
