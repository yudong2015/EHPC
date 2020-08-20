#!/usr/bin/env python

import sys
import json

from common import logger, response
from constants import (
    ACTION_ADD,
    ACTION_LIST,
    ACTION_DELETE,
    HOME_DIR_FMT,
    LDAP_NOT_EXIST_ERROR,
)

from ldap import LDAPError
from ldap_utils import new_ldap_client


def help():
    print 'usage: userctl {"action": get / add / delete, "user_name": "uxxx", ' \
          ' "user_id": 1100, "group_id": 1100, "parent_uid"}'


def get_user():
    client = None
    try:
        client = new_ldap_client()
        ret = client.list_user()
        users = []
        for u in ret:
            if u[1].get("cn", None):
                users.append(u[1]["cn"])
        return response(True, {"user_list": users})
    except Exception as e:
        logger.error("list user failed: [%s]", e.message)
        return response(False)
    finally:
        if client:
            client.close()


def add_user(params):
    parent_user_id = params.get("parent_user_id", None)
    user_name = params.get("user_name", None)
    password = params.get("password", None)
    group_name = params.get("group_name", parent_user_id)
    group_id = params.get("group_id", None)
    if parent_user_id and user_name and password and group_id:
        client = None
        try:
            client = new_ldap_client()
            if client.user_exist(user_name):
                return response(False, "The user[%s] already exist.".format(user_name))

            if not client.group_exist(group_id):
                client.create_group(group_name, group_id)

            uid = client.generate_uid_number()
            home_dir = HOME_DIR_FMT.format(parent_user_id, user_name)
            client.create_user(user_name, uid, password, home_dir, group_id)
            return response(True)
        except Exception as e:
            logger.error("Failed to create user: [%s]", e.message)
            return response(False)
        finally:
            if client:
                client.close()
    else:
        err_msg = "Require params: parent_user_id: [%s], user_name: [%s], " \
                  "group_id: [%s]".format(parent_user_id, user_name, group_id)
        logger.error(err_msg)
        return response(False, err_msg)


def delete_user(params):
    user_name = params.get("user_name", None)
    if not user_name:
        return response(False, "required params: user_name[%s].".format(user_name))
    client = None
    try:
        client = new_ldap_client()
        client.delete_user(user_name)
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
        if client:
            client.close()


def main(argv):
    if len(argv) < 2:
        help()
        sys.exit(1)
    else:
        args = json.loads(argv[1])

    action = args.get("action", None)

    if action == ACTION_LIST:
        return get_user()
    elif action == ACTION_ADD:
        return add_user(args)
    elif action == ACTION_DELETE:
        return delete_user(args)
    else:
        help()
        return response("The can not handle the action[{}].".format(action))


if __name__ == "__main__":
    main(sys.argv)
