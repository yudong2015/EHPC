#!/usr/bin/env python

import sys
import traceback

from common import (
    logger,
    response,
    json_loads,
    get_admin_info,
)
from constants import (
    ACTION_USER_ADD,
    ACTION_USER_ADD_ADMIN,
    ACTION_USER_LIST,
    ACTION_USER_DELETE,
    ACTION_RESET_PASSWORD,

    ADMIN_HOME_FMT,
    HOME_FMT,
    LDAP_NOT_EXIST_ERROR,
)

from ldap import LDAPError
from ldap_utils import new_ldap_client


def get_user():
    ldap_client = None
    try:
        ldap_client = new_ldap_client()
        ret = ldap_client.list_user()
        users = [u[1]["cn"] for u in ret if u[1].get("cn", None)]
        return response(True, {"user_list": users})
    except Exception as e:
        logger.error("list user failed: [%s]", e.message)
        return response(False)
    finally:
        if ldap_client:
            ldap_client.close()


def add_user(params):
    user_name = params.get("user_name", None)
    password = params.get("password", None)
    if user_name and password:
        ldap_client = None
        try:
            ldap_client = new_ldap_client()
            if ldap_client.user_exist(user_name):
                return response(False, "The user[{}] already exist.".format(user_name))

            admin_info = get_admin_info()
            gid = admin_info["group_id"]
            # gname = admin_info["admin_user"]
            # if not ldap_client.group_exist(gid):
            #     ldap_client.create_group(gname, gid)

            uid = ldap_client.generate_uid_number()
            home_dir = HOME_FMT.format(admin_info["nas_path"], user_name)
            ldap_client.create_user(user_name, uid, password, home_dir, gid)
            return response(True)
        except Exception:
            logger.error("Failed to create user: [%s]", traceback.format_exc())
            return response(False)
        finally:
            if ldap_client:
                ldap_client.close()
    else:
        err_msg = "Require params: user_name: [%s], password: [%s]".\
            format(user_name, password)
        logger.error(err_msg)
        return response(False, err_msg)


def add_admin_user():
    ldap_client = new_ldap_client()
    admin_info = get_admin_info()

    gid = admin_info["group_id"]
    gname = admin_info["admin_user"]
    ldap_client.create_group(gname, gid)

    home_dir = ADMIN_HOME_FMT.format(admin_info["nas_path"])
    ldap_client.create_user(admin_info["admin_user"],
                            admin_info["admin_user"],
                            admin_info["password"], home_dir, gid)
    ldap_client.close()


def delete_user(params):
    user_name = params.get("user_name", None)
    if not user_name:
        return response(False, "required params: user_name[{}].".
                        format(user_name))

    if user_name == get_admin_info()["admin_user"]:
        logger.error("The admin user[%s] can not be deleted.", user_name)
        return response(False, "invalid user name")

    ldap_client = None
    try:
        ldap_client = new_ldap_client()
        ldap_client.delete_user(user_name)
        return response(True)
    except LDAPError as e:
        logger.error("ldap error with deleting user[%s]: [%s]", user_name, e.message)
        if e.message.get("result", 0) == LDAP_NOT_EXIST_ERROR:
            return response(False, "The user[%s] not exist.".format(user_name))
        raise e
    except Exception as e:
        logger.error("Failed to delete user[%s]: [%s]", user_name, e.message)
        return response(False)
    finally:
        if ldap_client:
            ldap_client.close()


def reset_password(params):
    user_name = params.get("user_name", None)
    password = params.get("password", None)
    new_password = params.get("new_password", None)
    if user_name and password and new_password:
        if password == new_password:
            logger.warning("The same password, skip")
            return response(False, "The same password, skip")

        ldap_client = None
        try:
            ldap_client = new_ldap_client()
            ldap_client.reset_password(user_name, password, new_password)
        except Exception:
            logger.error("Failed reset password of user[%s]: [%s]",
                         user_name, traceback.format_exc())
            return response(False)
        finally:
            if ldap_client:
                ldap_client.close()
    else:
        logger.error("lack param.")


def main(argv):
    if len(argv) < 2:
        return response(False, "lack param.")
    else:
        action = argv[1]

    if action == ACTION_USER_LIST:
        return get_user()
    else:
        args = json_loads(argv[2])
        if not args:
            return response(False)

        if action == ACTION_USER_ADD:
            return add_user(args)
        elif action == ACTION_USER_ADD_ADMIN:
            add_admin_user()
        elif action == ACTION_USER_DELETE:
            return delete_user(args)
        elif action == ACTION_RESET_PASSWORD:
            return reset_password(args)
        else:
            return response(False, "The can not handle the action[{}].".format(action))


# usage: userctl get/add/delete {"user_name": "uxxx", "user_id": 1100, "group_id": 1100, "parent_uid"}
if __name__ == "__main__":
    res = main(sys.argv)
