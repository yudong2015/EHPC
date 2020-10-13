#!/usr/bin/env python

import sys
import subprocess
import traceback
import simplejson as jsmod
from datetime import datetime
from os import path as os_path
import logging
from logging.handlers import RotatingFileHandler

from constants import (
    CLUSTER_INFO_FILE,
    BACKUP_DIR,
    LOG_DIR,
    LOG_FILE,
    COMPUTE_HOSTNAME_PREFIX,
    ROLE_COMPUTE,
    ACTION_PARAM_CONF,
)

# create log dir
if not os_path.exists(LOG_DIR):
    subprocess.check_call("mkdir -p {}".format(LOG_DIR).split(" "))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formater = logging.Formatter(
    '[%(asctime)s] - %(levelname)s - %(message)s [%(pathname)s:%(lineno)d]')
ehpc_handler = RotatingFileHandler(LOG_FILE, mode="w", maxBytes=100000000,
                                   backupCount=3, encoding="utf-8")
ehpc_handler.setFormatter(formater)
ehpc_handler.setLevel(logging.DEBUG)

logger.addHandler(ehpc_handler)

CLUSTER_INFO = {}


def backup(cmd):
    run_shell("mkdir -p {}".format(BACKUP_DIR))
    # cmd with fmt for time
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    run_shell(cmd.format(now))


def run_shell(cmd, without_log=False):
    if not without_log:
        logger.info("Run cmd[%s]...", cmd)
    return subprocess.check_call(cmd.split(" "))


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


def get_cluster_info():
    global CLUSTER_INFO
    if not CLUSTER_INFO:
        CLUSTER_INFO = json_load(CLUSTER_INFO_FILE, True)
    return CLUSTER_INFO


def get_role():
    cluster_info = get_cluster_info()
    role = cluster_info.get("role")
    if role:
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


class ArgsParser(object):

    def __init__(self):
        self.action = ""
        self.directive = {}

    def parse(self, args):
        logger.info("parse args: [%s]", args)
        if len(args) < 2:
            logger.error("parameter[%s] is not complete(action needed)!")
            return False

        self.action = args[1]
        if len(args) > 2:
            self.directive = json_loads(args[2]) or {}
        return self._check()

    def _check(self):
        if self.action in ACTION_PARAM_CONF:
            conf = ACTION_PARAM_CONF[self.action]
            return self._check_required_params(conf.get("required") or []) \
                   and self._check_list_params(conf.get("list_params") or []) \
                   and self._check_json_params(conf.get("json_params") or [])
        else:
            self.directive = {}  # clear directive that there is no param
        return True

    def _check_list_params(self, params):
        for param in params:
            if param not in self.directive:
                continue
            if not isinstance(self.directive[param], list):
                logger.error("parameter[%s] should be list in directive[%s]",
                             param, self.directive)
                return False
        return True

    def _check_json_params(self, params):
        for param in params:
            if not self.directive.get(param) or \
                    isinstance(self.directive[param], dict):
                continue
            else:
                if not isinstance(self.directive[param], str):
                    logger.error("parameter[%s] should be str in "
                                 "directive[%s]", param, self.directive)
                    return False
                obj = json_load(self.directive[param].replace("\'", '"'))
                if obj is None:
                    logger.error("parameter[%s] should be json str in "
                                 "directive[%s]", param, self.directive)
                    return False
                self.directive[param] = obj
        return True

    def _check_required_params(self, params):
        for param in params:
            if param not in self.directive:
                logger.error("param[%s] should be specified in directive[%s]",
                             param, self.directive)
                return False
        return True






