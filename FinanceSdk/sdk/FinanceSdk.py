# -*- coding: utf-8 -*-

import json
import base64
import logging
import platform
import ctypes
import os
from ctypes import (
    Structure,
    c_int,
    c_void_p,
    CDLL,
    c_char_p,
    c_ulonglong,
    c_ulong,
    byref,
    string_at,
)
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto import Random


from .exceptions import (
    FinanceSdkInitException,
    FinanceSdkGetChatDataException,
    FinanceSdkDecryptException,
    FinanceSdkGetMediaDataException,
)
import logging

_logger = logging.getLogger(__name__)


class Slice(Structure):
    _fields_ = [("buf", c_void_p), ("len", c_int)]


class Media(Structure):
    _fields_ = [
        ("outindexbuf", c_void_p),
        ("out_len", c_int),
        ("data", c_void_p),
        ("data_len", c_int),
        ("is_finish", c_int),
    ]


class FinanceSdk(object):
    def __init__(self,):
        self.dll = None
        self.sdk = None
        self.ciphers = []

        lib_path = ""
        if platform.system() == "Windows":
            # windows平台
            lib_path = f"{os.path.dirname(os.path.realpath(__file__))}/windows/WeWorkFinanceSdk.dll"
        else:
            # 非window平台
            lib_path = f"{os.path.dirname(os.path.realpath(__file__))}/linux/libWeWorkFinanceSdk_C.so"
        self.dll = CDLL(lib_path)

    def init_finance_sdk(self, corpid, secret, private_keys):
        self.corpid = corpid
        self.secret = secret
        self.private_keys = private_keys

        for key in self.private_keys:
            key_dict = {}
            key_dict["publickey_ver"] = key.publickey_ver

            key_dict["private_key"] = PKCS1_v1_5.new(RSA.importKey(key.private_key))
            self.ciphers.append(key_dict)

        dll = self.dll
        self.dll.NewSdk.restype = c_void_p
        sdk = dll.NewSdk()
        if isinstance(self.corpid, str):
            corpid = self.corpid.encode()
        if isinstance(self.secret, str):
            secret = self.secret.encode()
        result = dll.Init(c_void_p(sdk), c_char_p(corpid), c_char_p(secret))
        if result != 0:
            _logger.error(
                "Session content archiving sdk init fail. result:%s" % result
            )
            raise FinanceSdkInitException(result, "Init fail")
        else:
            _logger.info("Session content archiving sdk init success")
            self.sdk = sdk
            # if platform.system() == "Windows":
            #     return self
            # else:
            #     return self.sdk

        return self

    def destroy_sdk(self):
        """
        释放sdk，和 NewSdk 成对使用
        """
        self.dll.DestroySdk(c_void_p(self.sdk))  # 释放sdk，和 NewSdk 成对使用
        _logger.info("Session content archiving sdk released success")

    def get_chatdata(self, seq, limit=1000):
        """
        获取聊天记录

        :param seq: 消息顺序号
        :param limit: 一次拉取的消息条数，最大值1000条，超过1000条会返回错误
        :return:
        """

        slice = Slice()
        # 获取聊天记录
        result = self.dll.GetChatData(
            c_void_p(self.sdk),  # NewSdk返回的sdk指针
            c_ulonglong(
                seq
            ),  # 从指定的seq开始拉取消息，注意的是返回的消息从seq+1开始返回，seq为之前接口返回的最大seq值。首次使用请使用seq:0
            c_ulong(limit),  # 一次拉取的消息条数，最大值1000条，超过1000条会返回错误
            c_char_p(
                None
            ),  # 使用代理的请求，需要传入代理的链接。如：socks5://10.0.0.1:8081 或者 http://10.0.0.1:8081
            c_char_p(None),  # 代理账号密码，需要传入代理的账号密码。如 user_name:passwd_123
            c_int(10),  # 超时时间，单位秒
            byref(slice),  # 返回本次拉取消息的数据.密文消息，slice结构体
        )
        if result != 0:
            _logger.error("Failed to get chat data,result:%s") % result
            raise FinanceSdkGetChatDataException(result, "Failed to get chat data")

        chats_data = json.loads(string_at(slice.buf, slice.len))  # 聊天数据响应
        # _logger.info(_("get chat data response:%s") % chats_data)
        for chat in chats_data["chatdata"]:
            # 解密数据
            chat_msg = self.decrypt_chatdata(
                chat["publickey_ver"],
                chat["encrypt_random_key"],
                chat["encrypt_chat_msg"],
            )
            chat["decrypted_chat_msg"] = chat_msg

        self.destroy_sdk()  # 完成获取聊天记录后，释放sdk，和 NewSdk 成对使用
        return chats_data["chatdata"]

    def get_cipher(self, version):
        if len(self.ciphers) == 0:
            return None
        else:
            for cipher in self.ciphers:
                if cipher["publickey_ver"] == version:
                    return cipher["private_key"]

    def decrypt_chatdata(self, publickey_ver, encrypt_random_key, encrypt_chat_msg):
        """
        解密聊天数据
        """
        dsize = SHA.digest_size
        sentinel = Random.new().read(15 + dsize)
        encrypt_random_key = base64.b64decode(encrypt_random_key)

        cipher = self.get_cipher(publickey_ver)
        if not cipher:
            _logger.warning(
                "public key version %s not loaded, can't decrypt" % publickey_ver
            )
            raise FinanceSdkDecryptException(
                -1, "public key version %s not loaded" % publickey_ver
            )

        # decrypted_key = ciphers[publickey_ver - 1].decrypt(encrypt_random_key, sentinel)
        decrypted_key = cipher.decrypt(encrypt_random_key, sentinel)

        _logger.info(
            "version:%s encrypt_random_key:%s decrypted_key:%s"
            % (decrypted_key, encrypt_random_key, decrypted_key)
        )

        slice = Slice()
        ret = self.dll.DecryptData(
            c_char_p(decrypted_key), c_char_p(encrypt_chat_msg.encode()), byref(slice)
        )
        if ret != 0:
            _logger.error("decrypt chat msg fail due to %s" % ret)
            raise FinanceSdkDecryptException(ret, "DecryptData fail")

        return json.loads(string_at(slice.buf, slice.len))

    def get_mediadata(self, sdkfileid):
        """
        获取媒体文件数据（二进制）
        :param sdkfileid:
        :return:
        """
        if isinstance(sdkfileid, str):
            sdkfileid = sdkfileid.encode()

        data = b""
        media = Media()
        while True:
            ret = self.dll.GetMediaData(
                c_void_p(self.sdk),
                c_void_p(media.outindexbuf),
                c_char_p(sdkfileid),
                c_char_p(None),
                c_char_p(None),
                c_int(10),
                byref(media),
            )

            if ret != 0:
                _logger.error("get media data fail due to %s" % ret)
                raise FinanceSdkGetMediaDataException(ret, "GetMediaData fail")

            data += string_at(media.data, media.data_len)

            if media.is_finish:
                break
        return data

