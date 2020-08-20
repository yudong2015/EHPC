#!/usr/bin/env python

import subprocess
from constants import *
from datetime import datetime
from yaml import load, Loader
import logging


def backup(cmd):
    run_shell("mkdir -p {}".format(BACKUP_DIR))
    # cmd with fmt for time
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    run_shell(cmd.format(now))


def run_shell(cmd):
    print "Run cmd[{}]...".format(cmd)
    subprocess.check_call(cmd.split(" "))


def get_role():
    with open(ROLE_INFO, 'r') as info:
        role = info.read().strip()
    if role:
        print "The role is: {}".format(role)
        return role
    else:
        print "The role is none!"
        exit(1)


def get_hostname():
    role = get_role()
    if role == ROLE_COMPUTE:
        with open(CMP_SID_INFO, "r") as info:
            sid = info.read().strip()
        return "{}{}".format(COMPUTE_HOSTNAME_PREFIX, sid)
    else:
        return role


def yaml_load(stream):
    ''' load from yaml stream and create a new python object

    @return object or None if failed
    '''
    try:
        obj = load(stream, Loader=Loader)
    except Exception, e:
        obj = None
        print("load yaml failed: ")
        print e
    return obj


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


logging.basicConfig(
    format='[%(asctime)s] - %(levelname)s: %(message)s [%(pathname)s:%(lineno)d]',
    level=logging.INFO)

logger = logging.getLogger(__name__)
