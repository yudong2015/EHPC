#!/usr/bin/env python

import os
import sys
import traceback

from common import (
    logger,
    ArgsParser,
    run_shell,
    get_cluster_info,
)
from constants import (
    ACTION_SOFTWARE_INSTALL,
    ACTION_SOFTWARE_UNINSTALL,

)

SOFTWARE_WORKDIR = "/tmp/software"
SOFTWARE_HOME_FMT = "/home/{}/opt"


# software format:
#   [{
#     "name": xxx,     name must be same as install dir and dir after un-tar
#     "source": xxx,
#     "installer": xxx, Run: [SOFTWARE_HOME]/[installer]
#   }]
def install(software):
    logger.info("install software[%s]..", software)
    run_shell("mkdir -p {}".format(SOFTWARE_WORKDIR))
    software_home = get_software_home()
    for s in software:
        if os.path.exists("{}/{}".format(software_home, s)):
            logger.error("The software[%s] already exist!", s)
            sys.exit(55)

    for s in software:
        _install(s["name"], s["source"], software_home, s.get("installer"))


def _install(software, source, software_home, installer=None):
    """
    :param source: full url to download software, eg: root@xxx/aa/bb/cc.tar.gz
    :param software_home: the home that software would to be installed
    :param software: software name (install dir: software_home/software)
    :param installer: install script
    :return:
    """
    logger.info("Do install software[%s] from source[%s]..", software, source)

    package = source.split("/")[-1]
    un_tar_dir = "{}/{}".format(SOFTWARE_WORKDIR, software)

    if installer:
        installer = "bash {}".format(installer)
    else:
        f = "bash {}/install.sh".format(un_tar_dir)
        installer = f if os.path.exists(f) else \
            "mv {} {}/".format(un_tar_dir, software_home)

    try:
        # download
        run_shell("rsync -q -aP {} {}/".format(source, SOFTWARE_WORKDIR))
        # un-tar
        run_shell("tar -zxf {}/{}".format(SOFTWARE_WORKDIR, package))
        # install
        run_shell("export SOFTWARE_HOME={} && {}".format(software_home, installer))
    except Exception as e:
        logger.error("Failed to run install cmd: %s", e.message)
        logger.error("Error: %s", traceback.format_exc())
        sys.exit(1)


# software format:
#   [{
#     "name": xxx,     name must be same as install dir and dir after un-tar
#     "uninstaller": xxx
#   }]
def uninstall(software):
    logger.info("uninstall software[%s]..", software)
    software_home = get_software_home()
    for s in software:
        if not os.path.exists("{}/{}".format(software_home, s)):
            logger.error("The software[%s] not exist!", s)
            sys.exit(54)

    for s in software:
        _uninstall(s["name"], software_home, s.get("uninstaller"))


def _uninstall(software, software_home, uninstaller=None):
    logger.info("Do uninstall software[%s]..", software)
    software_dir = "{}/{}".format(software_home, software)
    if uninstaller:
        uninstaller = "bash {}".format(uninstaller)
    else:
        f = "bash {}/uninstall.sh".format(software_dir)
        uninstaller = f if os.path.exists(f) else "rm -rf {}".format(software_dir)

    try:
        # uninstall
        run_shell("export SOFTWARE_HOME={} && {}".format(software_home, uninstaller))
    except Exception as e:
        logger.error("Failed to run install cmd: %s", e.message)
        logger.error("Error: %s", traceback.format_exc())
        sys.exit(1)


def get_software_home():
    cluster_info = get_cluster_info()
    return SOFTWARE_HOME_FMT.format(cluster_info["admin_user"])


def help():
    print "softwarectl install [{name: xxx, source: xxx, installer: xxxx}, ..]\n"
    print "            uninstall [{name: xxxx, uninstaller: xxx}]\n"


ACTION_MAP = {
    "help": help,
    "--help": help,
    ACTION_SOFTWARE_INSTALL: install,
    ACTION_SOFTWARE_UNINSTALL: uninstall,
}


# could use env [SOFTWARE_HOME] in install or uninstall script
def main(argv):
    try:
        parser = ArgsParser()
        ret = parser.parse(argv)
        if not ret:
            sys.exit(40)

        if parser.action in ACTION_MAP:
            if parser.directive:
                ACTION_MAP[parser.action](parser.directive["software"])
            else:
                ACTION_MAP[parser.action]()
        else:
            logger.error("can not handle the action[%s].", parser.action)
            sys.exit(40)
    except Exception:
        logger.error("Failed to update software: [%s]", traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
