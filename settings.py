# -*- coding: utf-8 -*-
# Copyright 2013 Gully Chen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Site Settings for various runtime environments
"""


# Global Settings

import os
import sys
import logging


__version__ = "3"

######################################
# Global environment
######################################

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "libs"))


class MagicDict(dict):
    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)
        self.__dict__ = self

    def __getattr__(self, name):
        self[name] = MagicDict()
        return self[name]


try:
    from google.appengine.api import conf
    _, _, GAE_DEVELOPMENT = conf._inspect_environment()

    RUNTIME_ENV = "gae"
    if GAE_DEVELOPMENT:
        RUNTIME_ENV = "gae_dev"

except:
    RUNTIME_ENV = "local"

    server = os.environ.get("SERVER_SOFTWARE", "")
    if server.startswith("bae"):
        RUNTIME_ENV = "bae"

        from bae_utils.log import getLogger
        logging = getLogger("bae.debug.log")

    elif server.startswith("direwolf"):
        RUNTIME_ENV = "sae"


from flask import Flask


######################################
# Application
######################################
app = Flask(__name__)

app.config["APP_VER"] = __version__
app.config["SiteTitle"] = u"藏羚羊"
app.config["SiteSubTitle"] = "follow your heart"
app.config["OwnerEmail"] = "583695898@qq.com"
app.config["DefaultPassword"] = "ZHANG1993991"

app.config["RUNTIME_ENV"] = RUNTIME_ENV

if RUNTIME_ENV == "bae":
    const = MagicDict()
    const.APP_ID = "appidl85v1410e1"
    const.ACCESS_KEY = "517557c6fa47408e810f409152a2fe09"
    const.SECRET_KEY = "ee0ebcd1f9034e7d812cfd2dcbf3624c"

    const.CACHE_ID = "bTXWvXunneyHgLlmglxn"
    const.CACHE_USER = const.ACCESS_KEY
    const.CACHE_PASS = const.SECRET_KEY
    const.CACHE_HOST = "cache.duapp.com"
    const.CACHE_PORT = "20243"
    const.CACHE_ADDR = "%s:%s" % (const.CACHE_HOST, const.CACHE_PORT)

    const.MYSQL_DATABASE = "ZWWoOkTkitIIepKsNUzj"
    const.MYSQL_USER = const.ACCESS_KEY
    const.MYSQL_PASS = const.SECRET_KEY
    const.MYSQL_HOST = "sqld.duapp.com"
    const.MYSQL_PORT = "4050"
    '''
    const.BCS_ADDR = "http://bcs.duapp.com/"
    const.BCS_USER = const.ACCESS_KEY
    const.BCS_PASS = const.SECRET_KEY
    const.BCS_BUCKET = "chenyangblog"
    '''
    const.BUCKET_NAME = 'chenyangblog'
    const.BOS_FOLDER = "/photos/"
    const.BOS_HOST = "http://bj.bcebos.com"
    const.ACCESS_KEY_ID = const.ACCESS_KEY
    const.SECRET_ACCESS_KEY = const.SECRET_KEY

    app.config["BAE_CONFIG"] = const

elif RUNTIME_ENV == "sae":
    import sae.const as sae_const
    const = MagicDict()

    const.APP_ID = os.environ.get("APP_NAME", "N/A")

    const.ACCESS_KEY = sae_const.ACCESS_KEY
    const.SECRET_KEY = sae_const.SECRET_KEY

    const.MYSQL_DATABASE = sae_const.MYSQL_DB
    const.MYSQL_USER = sae_const.MYSQL_USER
    const.MYSQL_PASS = sae_const.MYSQL_PASS
    const.MYSQL_HOST = sae_const.MYSQL_HOST
    const.MYSQL_PORT = sae_const.MYSQL_PORT

    const.SAE_BUCKET = "deepgully"
    const.SAE_FOLDER = "/photos/"

    app.config["SAE_CONFIG"] = const


######################################
# Database
######################################
if RUNTIME_ENV in ("bae", "sae"):
    app.secret_key = const.ACCESS_KEY + const.SECRET_KEY

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (
        const.MYSQL_USER, const.MYSQL_PASS,
        const.MYSQL_HOST, const.MYSQL_PORT,
        const.MYSQL_DATABASE
    )

    app.config['SQLALCHEMY_POOL_RECYCLE'] = 10

elif RUNTIME_ENV in ("local",):
    LOCAL_DATABASE = "chenyangblog"

    app.secret_key = "ee0ebcd1f9034e7d812cfd2dcbf3624c"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s.db' % LOCAL_DATABASE
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1:3306/%s' % LOCAL_DATABASE

elif RUNTIME_ENV in ("gae", "gae_dev"):

    app.secret_key = "ee0ebcd1f9034e7d812cfd2dcbf3624c+GAE"


if RUNTIME_ENV in ("bae", "sae", "local"):
    from alembic.config import Config
    MIGRATE_CFG = Config(os.path.join(BASE_DIR, "alembic.ini"))
    MIGRATE_CFG.set_section_option("alembic", "sqlalchemy.url", app.config['SQLALCHEMY_DATABASE_URI'])
    app.config['MIGRATE_CFG'] = MIGRATE_CFG


######################################
# User
######################################
from flask.ext.login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)


#####################################
# Mail
#####################################
if RUNTIME_ENV in ("bae", "sae"):
    pass
    #todo: support mail on BAE3 and SAE

elif RUNTIME_ENV in ("local",):
    app.config['MAIL_SERVER'] = "localhost"
    app.config['MAIL_PORT'] = 25
    app.config['MAIL_USE_TLS '] = False
    app.config['MAIL_USE_SSL '] = False
    app.config['MAIL_USERNAME '] = "test"
    app.config['MAIL_PASSWORD '] = "test"

    from flask_mail import Mail
    mail = Mail(app)

elif RUNTIME_ENV in ("gae", "gae_dev"):
    pass

#####################################
# Image Upload
#####################################
if RUNTIME_ENV in ("bae",):
    from baidubos.baidubce.bce_client_configuration import BceClientConfiguration
    from baidubos.baidubce.auth.bce_credentials import BceCredentials
    from baidubos.baidubce import exception
    from baidubos.baidubce.services import bos
    from baidubos.baidubce.services.bos import canned_acl
    from baidubos.baidubce.services.bos.bos_client import BosClient

    config = BceClientConfiguration(credentials=BceCredentials(const.ACCESS_KEY_ID, const.SECRET_ACCESS_KEY), endpoint = const.BOS_HOST)
    bos_client = BosClient(config)
    '''
    if not bos_client.does_bucket_exist(const.BUCKET_NAME):
        bos_client.create_bucket(const.BUCKET_NAME)
        #设置私有权限，只有owner有读写权限，其他人无权限
        bos_client.set_bucket_canned_acl(const.BUCKET_NAME, canned_acl.PRIVATE)
    '''
    '''
    pybcs_client = pybcs.HttplibHTTPC
    try:
        import pycurl
        pybcs_client = pybcs.PyCurlHTTPC
    except:
        pass

    BAE_BCS = pybcs.BCS(const.BCS_ADDR, const.BCS_USER, const.BCS_PASS, pybcs_client)
    BAE_BUCKET = BAE_BCS.bucket(const.BCS_BUCKET)
    '''

elif RUNTIME_ENV in ("sae",):
    from sae.storage import Bucket

    SAE_BUCKET = Bucket(const.SAE_BUCKET)

elif RUNTIME_ENV in ("local",):
    UPLOAD_URL = "static/uploads/"
    UPLOAD_FOLDER = os.path.join(app.root_path, UPLOAD_URL)

elif RUNTIME_ENV in ("gae", "gae_dev"):
    BLOB_SERVING_URL = "/_files"
    BLOB_UPLOAD_URL = "/_upload"
    app.config["BLOB_SERVING_URL"] = BLOB_SERVING_URL
    app.config["BLOB_UPLOAD_URL"] = BLOB_UPLOAD_URL


QINIU_SETTINGS = MagicDict()

QINIU_SETTINGS.Enabled = False

if QINIU_SETTINGS.Enabled:
    QINIU_SETTINGS.ACCESS_KEY = "ef1ZZEwlvUzY-kBsp0jtWOf2rka0c_q8fnKMG8KP"
    QINIU_SETTINGS.SECRET_KEY = "XMM0GVgToJ3hhmVp9Vm-TDClfUe_IWOanqYSoM3a"

    QINIU_SETTINGS.BUCKET_NAME = "me-deepgully"
    QINIU_SETTINGS.BUCKET_DOMAIN = "me-deepgully.qiniudn.com"


app.config["QINIU"] = QINIU_SETTINGS


THUMB_SIZE = (400, 300)

app.config["THUMB_SIZE"] = THUMB_SIZE


######################################
# i18n
######################################
from flask.ext.babel import Babel
from flask.ext.babel import gettext, lazy_gettext
_ = gettext
babel = Babel(app)


def T(string):
    """ fake function for babel """
    return string


######################################
# memcache
######################################
ENABLE_MEMCACHE = True
if RUNTIME_ENV in ("bae",):
    ENABLE_MEMCACHE = True  # enable memcache for BAE3

elif RUNTIME_ENV in ("sae",):
    ENABLE_MEMCACHE = True   # enbale memcache for SAE

elif RUNTIME_ENV in ("local",):
    app.config['MEMCACHE_SERVERS'] = ["127.0.0.1:11211", ]

