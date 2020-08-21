#!/usr/bin/env python

import sys
from os import path
from constants import (
    ACTION_APP_INIT,
    ACTION_APP_START,
    ACTION_APP_STOP,
    ACTION_APP_RESTART,
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


def init():
    logger.info("Generating hosts...")
    generate_hosts()

    logger.info("Setup hostname...")
    set_hostname()

    logger.info("Generating hosts for slurm configurations...")
    generate_conf()
    logger.info("Init done.")


def controller_start():
    run_shell("systemctl start slurmctld")
    run_shell("systemctl start slapd")
    # create admin user
    run_shell("userctl {}".format(ACTION_USER_ADD_ADMIN))


def compute_start():
    run_shell("systemctl start slurmd")
    run_shell("systemctl start nslcd")
    clear_files = ["/usr/sbin/userctl"]
    for f in clear_files:
        if path.exists(f):
            run_shell("rm {}".format(f))


def login_start():
    run_shell("systemctl start nslcd")
    clear_files = ["/usr/sbin/userctl"]
    for f in clear_files:
        if path.exists(f):
            run_shell("rm {}".format(f))


def start():
    role = get_role()
    if role == ROLE_CONTROLLER:
        controller_start()
    elif role == ROLE_COMPUTE:
        compute_start()
    elif role == ROLE_LOGIN:
        login_start()
    else:
        logger.error("Unsupport role[%s].", role)
        sys.exit(1)


def restart():
    pass


def stop():
    role = get_role()
    if role == ROLE_CONTROLLER:
        run_shell("systemctl stop slurmctld")
        run_shell("systemctl stop slapd")
    elif role == ROLE_COMPUTE:
        run_shell("systemctl stop slurmd")
        run_shell("systemctl stop nslcd")
    elif role == ROLE_LOGIN:
        run_shell("systemctl stop nslcd")
    else:
        logger.error("Unsupport role[%s].", role)
        sys.exit(1)


def help():
    logger.info("usage: appctl init/start/stop")


def main(argv):
    if len(argv) < 2:
        help()
        sys.exit(1)
    else:
        action = argv[1]

    if action == ACTION_APP_INIT:
        init()
    elif action == ACTION_APP_START:
        start()
    elif action == ACTION_APP_STOP:
        stop()
    elif action == ACTION_APP_RESTART:
        restart()
    else:
        help()
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
