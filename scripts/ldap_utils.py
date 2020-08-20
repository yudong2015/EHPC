#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import (
    logger,
    yaml_load,
)
import ldap
from ldap import modlist

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

GROUP_SEARCH_ATTRS = ["gidNumber", "cn"]
USER_SEARCH_ATTRS = ["cn", "uidNumber", "gidNumber"]


class LdapClient(object):
    def __init__(self, ldap_address, parent_dn, admin, passwd):
        self.address = ldap_address
        self.parent_dn = parent_dn
        self.bind_dn = "cn={},{}".format(admin, parent_dn)
        self.passwd = passwd

        self.user_ou = "People"
        self.user_object_class = [
            "posixAccount",
            "inetOrgPerson",
            "shadowAccount"
        ]
        self.user_base_dn = "ou={},{}".format(self.user_ou, parent_dn)

        self.group_ou = "Group"
        self.group_object_class = ["posixGroup"]
        self.group_base_dn = "ou={},{}".format(self.group_ou, parent_dn)

        self.ldap_object = None

    def connect(self):
        if self.ldap_object is None:
            logger.info("Connecting ldap server..")
            self.ldap_object = ldap.initialize(self.address)
            self.ldap_object.protocol_version = ldap.VERSION3
            self.ldap_object.set_option(ldap.OPT_REFERRALS, 0)
            self.ldap_object.simple_bind_s(self.bind_dn, self.passwd)
            logger.info("connected.")
        return self.ldap_object

    def close(self):
        if self.ldap_object is not None:
            self.ldap_object.unbind_s()

    def create_user(self, user_name, uid, password, home_dir, gid):
        logger.info("create user, home: [%s], name: [%s], uid: [%s], "
                    "gid: [%s], pwd: [%s]", home_dir, user_name, uid,
                    gid, password)
        attrs = dict(
            sn=user_name,
            cn=user_name,  # common name
            uid=user_name,
            uidNumber=uid,
            gidNumber=gid,
            userPassword=password,
            ou=self.user_ou,  # People
            homeDirectory=home_dir,
            loginShell="/bin/bash",
            objectClass=self.user_object_class  # ['posixAccount','inetOrgPerson'] #cn、sn必填
        )
        dn = "cn={cn},ou={ou},{parent_dn}".format(
            cn=user_name, ou=self.user_ou, parent_dn=self.parent_dn)
        ldif = modlist.addModlist(attrs)
        res = self.ldap_object.add_s(dn, ldif)
        logger.info("create user response: [%s]", res)
        logger.info("create user successfully.")

        #创建用户实体先默认不设置密码，直接在创建用户实体设置密码属性，初始密码是未加密形式保存？
        #创建用户实体，设置成密码模式保存
        #password = 'oA@10-14'
        #res = modify_password(dn, None, password)
        #print("modify_password done.")

    def create_group(self, g_name, gid):
        logger.info("create group, name: [%s], gid: [%s]", g_name, gid)
        attrs = dict(
            cn=g_name,  # common name
            memberUid=g_name,
            gidNumber=gid,
            objectClass=self.group_object_class,
        )
        dn = "cn={cn},ou={ou},{parent_dn}".format(
            cn=g_name, ou=self.group_ou, parent_dn=self.parent_dn)
        ldif = modlist.addModlist(attrs)
        res = self.ldap_object.add_s(dn, ldif)
        logger.info("Create group response: [%s]", res)
        logger.info("create group successfully.")

    # ldap search response with default attributes: [
    #     ('ou=People,dc=ehpccloud,dc=com', {'objectClass': ['organizationalUnit'], 'ou': ['People']}),
    #
    #     ('cn=tuser,ou=People,dc=ehpccloud,dc=com',
    #      {'uid': ['tuser'], 'objectClass': ['posixAccount', 'inetOrgPerson', 'shadowAccount'],
    #       'loginShell': ['/bin/bash'], 'userPassword': ['Zhu1241jie'], 'uidNumber': ['1101'], 'gidNumber': ['1101'],
    #       'sn': ['tuser'], 'homeDirectory': ['/home/usr-xxxxx/tuser'], 'ou': ['People'], 'cn': ['tuser']}),
    #
    #     ('cn=tuser2,ou=People,dc=ehpccloud,dc=com',
    #      {'uid': ['tuser2'], 'objectClass': ['posixAccount', 'inetOrgPerson', 'shadowAccount'],
    #       'loginShell': ['/bin/bash'], 'userPassword': ['Zhu1241jie'], 'uidNumber': ['1102'], 'gidNumber': ['1102'],
    #       'sn': ['tuser2'], 'homeDirectory': ['/home/usr-xxxxx/tuser2'], 'ou': ['People'], 'cn': ['tuser2']}),
    # ]
    def list_user(self, user_name=""):
        logger.info("list user ..")
        search_filter = None
        if user_name:
            search_filter = "cn={}".format(user_name)
        ret = self.ldap_object.search_s(self.user_base_dn, ldap.SCOPE_SUBTREE,
                                        search_filter, USER_SEARCH_ATTRS)
        logger.info("search user response: [%s]", ret)
        return ret

    def user_exist(self, user_name, user_id=None):
        logger.info("Check if user name exist..")
        search_filter = "cn={}".format(user_name)
        ret = self.ldap_object.search_s(
            self.user_base_dn, ldap.SCOPE_SUBTREE,
            search_filter, USER_SEARCH_ATTRS)
        logger.info("Search user name response: [%s]", ret)
        for item in ret:
            if item[1].get("cn", None):
                return True

        if user_id:
            logger.info("Check if user id exist..")
            search_filter = "uidNumber={}".format(user_id)
            ret = self.ldap_object.search_s(
                self.user_base_dn, ldap.SCOPE_SUBTREE,
                search_filter, USER_SEARCH_ATTRS)
            logger.info("Search user id response: [%s]", ret)
            for item in ret:
                if item[1].get("uidNumber", None):
                    return True
        return False

    # search group response: [
    #   ('cn=tuser4,ou=Group,dc=ehpccloud,dc=com', {'gidNumber': ['1000'], 'cn': ['tuser4']})
    # ]
    def group_exist(self, g_id, g_name=""):
        logger.info("Check if group id exist..")
        search_filter = "gidNumber={}".format(g_id)
        ret = self.ldap_object.search_s(
            self.group_base_dn, ldap.SCOPE_SUBTREE,
            search_filter, GROUP_SEARCH_ATTRS)
        logger.info("Search group id response: [%s]", ret)
        for item in ret:
            if item[1].get("gidNumber", None):
                return True

        if g_name:
            logger.info("Check if group name exist..")
            search_filter = "cn={}".format(g_name)
            ret = self.ldap_object.search_s(
                self.group_base_dn, ldap.SCOPE_SUBTREE,
                search_filter, GROUP_SEARCH_ATTRS)
            logger.info("Search group name response: [%s]", ret)
            for item in ret:
                if item[1].get("cn", None):
                    return True
        return False

    def generate_uid_number(self):
        # generate uid not exist
        users = self.list_user()
        max_uid = 1000
        for user in users:
            for num_str in user[1].get("uidNumber", []):
                num = int(num_str)
                if num > max_uid:
                    max_uid = num
        return max_uid + 1

    def delete_user(self, user_name):
        logger.info("Delete user[%s]..", user_name)
        dn = "cn={cn},ou={ou},{parent_dn}".format(
            cn=user_name, ou=self.user_ou, parent_dn=self.parent_dn)
        res = self.ldap_object.delete_s(dn)
        logger.info("delete user response: [%s]", res)
        logger.info("deleted user successfully.")


def new_ldap_client():
    with open("ldap_conf.yaml", "r") as fs:
        conf = yaml_load(fs)
        if not conf:
            logger.error("The ldap configration is: [%s]", conf)
            return None
    return LdapClient(conf["address"], conf["parentDn"],
                      conf["admin"], conf["password"])
