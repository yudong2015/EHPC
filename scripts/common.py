#!/usr/bin/env python

import subprocess
from constants import (
    ROLE_INFO_FILE,
    CMP_SID_INFO_FILE,
    ENV_INFO_FILE,
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


def get_role():
    with open(ROLE_INFO_FILE, 'r') as info:
        role = info.read().strip()
    if role:
        logger.info("The role is: [%s].", role)
        return role
    else:
        logger.error("The role is none!")
        exit(1)


def get_hostname():
    role = get_role()
    if role == ROLE_COMPUTE:
        with open(CMP_SID_INFO_FILE, "r") as info:
            sid = info.read().strip()
        return "{}{}".format(COMPUTE_HOSTNAME_PREFIX, sid)
    else:
        return role


def json_loads(json_str):
    try:
        return jsmod.loads(json_str, encoding='utf-8')
    except Exception:
        logger.error("loads json str[%s] error: %s",
                     json_str, traceback.format_exc())
        return None


def get_admin_info():
    try:
        with open(ENV_INFO_FILE, "r") as e:
            info = jsmod.load(e)
        return info
    except Exception:
        logger.error("Failed to load env file: [%s]", traceback.format_exc())
        return None


# if success, the type of res must be dict
def response(success, res=None):
    if success:
        if not res:
            res = {}
        res["ret_code"] = 0
        return res
    else:
        if not res:
            res = "internal error"
        return {"ret_code": 1, "message": res}
