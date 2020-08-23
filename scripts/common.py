#!/usr/bin/env python

import sys
import subprocess
from constants import (
    CLUSTER_INFO_FILE,
    BACKUP_DIR,
    COMPUTE_HOSTNAME_PREFIX,
    ROLE_COMPUTE,
)
from datetime import datetime
import logging
import traceback
import simplejson as jsmod

logging.basicConfig(
    format='[%(asctime)s] - %(levelname)s: %(message)s [%(pathname)s:%(lineno)d]',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)


def backup(cmd):
    run_shell("mkdir -p {}".format(BACKUP_DIR))
    # cmd with fmt for time
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    run_shell(cmd.format(now))


def run_shell(cmd):
    logger.info("Run cmd[%s]...", cmd)
    subprocess.check_call(cmd.split(" "))


def json_load(json_file, err_exit=False):
    try:
        with open(json_file, "r") as fp:
            info = jsmod.load(fp)
        return info
    except Exception:
        logger.error("Failed to load file[%s]: [%s]", json_file,
                     traceback.format_exc())
        if err_exit:
            sys.exit(1)
        return None


def json_loads(json_str):
    try:
        return jsmod.loads(json_str, encoding='utf-8')
    except Exception:
        logger.error("loads json str[%s] error: %s",
                     json_str, traceback.format_exc())
        return None


CLUSTER_INFO = {}


def get_cluster_info():
    global CLUSTER_INFO
    if not CLUSTER_INFO:
        CLUSTER_INFO = json_load(CLUSTER_INFO_FILE, True)
    return CLUSTER_INFO


def get_role():
    cluster_info = get_cluster_info()
    role = cluster_info["role"]
    if role:
        logger.info("The role is: [%s].", role)
        return role
    else:
        logger.error("The role is none!")
        sys.exit(1)


def get_hostname():
    role = get_role()
    if role == ROLE_COMPUTE:
        cluster_info = get_cluster_info()
        return "{}{}".format(COMPUTE_HOSTNAME_PREFIX, cluster_info["sid"])
    else:
        return role
