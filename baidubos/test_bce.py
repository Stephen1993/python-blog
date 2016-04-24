#!/usr/bin/env python
#coding=utf-8

import logging
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials

from baidubce import exception
from baidubce.services import bos
from baidubce.services.bos import canned_acl
from baidubce.services.bos.bos_client import BosClient

bucket_name = 'chenyangblog'
bos_host = "http://bj.bcebos.com"
access_key_id = "517557c6fa47408e810f409152a2fe09"
secret_access_key = "ee0ebcd1f9034e7d812cfd2dcbf3624c"

logger = logging.getLogger('baidubce.services.bos.bosclient')
fh = logging.FileHandler('baidubos.log')
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)

config = BceClientConfiguration(credentials=BceCredentials(access_key_id, secret_access_key), endpoint = bos_host)
'''
#设置请求超时时间
config.connection_timeout_in_mills = TIMEOUT
#设置接收缓冲区大小
config.recv_buf_size(BUF_SIZE)
#设置发送缓冲区大小
bos_sample_conf.config.send_buf_size(BUF_SIZE)
#设置连接重试策略
#三次指数退避重试
config.retry_policy = BackOffRetryPolicy()
#不重试
config.retry_policy = NoRetryPolicy()
'''
bos_client = BosClient(config)

if not bos_client.does_bucket_exist(bucket_name):
        bos_client.create_bucket(bucket_name)
        #设置私有权限，只有owner有读写权限，其他人无权限
        bos_client.set_bucket_canned_acl(bucket_name, canned_acl.PRIVATE)

response = bos_client.list_buckets()
owner = response.owner
print 'user id:%s, user name:%s' % (owner.id, owner.display_name)
for bucket in response.buckets:
         print bucket.name

#查看bucket_name所属区域
print bos_client.get_bucket_location(bucket_name)

#bos_client.delete_bucket(bucket_name) #bucket不为空则删除失败
'''
#上传
bos_client.put_object(bucket_name, object_key, data) #data为流对象
bos_client.put_object_from_string(bucket_name, object_key, string) #string为字符串对象
bos_client.put_object_from_file(bucket_name, object_key, file_name) #file_name为文件
#查看bucket中的object列表
response = bos_client.list_objects(bucket_name)
for object in response.contents:
        print object.key
'''
