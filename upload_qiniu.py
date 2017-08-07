# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config


class upload_qiniu():
    def __init__(self):
        # 需要填写你的 Access Key 和 Secret Key
        access_key = 'lO44qI2dlzLylW5clwp-KUD8ve9Z_UHpi-7zCsho'
        secret_key = 'b2fJAuK9ACkEkpEcVpAk1DyTdQXhb6WDnB7h8pHT'
        # 构建鉴权对象
        self.q = Auth(access_key, secret_key)
        # 要上传的空间
        self.bucket_name = 'inst'
        # 上传到七牛后保存的文件名

    def upload(self, key, path):
        # 生成上传 Token，可以指定过期时间等
        token = self.q.upload_token(self.bucket_name, key, 3600)
        # 要上传文件的本地路径
        ret, info = put_file(token, key, path)
        print(info)
        assert ret['key'] == key
        assert ret['hash'] == etag(path)


# uq = upload_qiniu()
# uq.upload('t.py', 'main.py')
