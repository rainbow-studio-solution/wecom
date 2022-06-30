# -*- coding: utf-8 -*-

import json
import requests
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError
import warnings


class ApiException(Exception):
    def __init__(self, errCode, errMsg):
        super().__init__(errCode, errMsg)
        self.errCode = errCode
        self.errMsg = errMsg


class WecomAbstractApi(models.AbstractModel):
    _name = "wecom.abstract_api"
    _description = "Wecom Abstract API"

    code = fields.Integer("API error code", copy=False)
    message = fields.Char("API error message", copy=False)

    def get_api_debug(self):
        """
        获取 API 调试模式
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        return True if ir_config.get_param("wecom.debug_enabled") == "True" else False

    def getAccessToken(self):
        raise NotImplementedError

    def refreshAccessToken(self):
        raise NotImplementedError

    def getSuiteAccessToken(self):
        raise NotImplementedError

    def refreshSuiteAccessToken(self):
        raise NotImplementedError

    def getProviderAccessToken(self):
        raise NotImplementedError

    def refreshProviderAccessToken(self):
        raise NotImplementedError

    def httpCall(self, urlType, args=None, include_agentid=False):
        """
        调用API
        :param urlType : 服务端API类型和请求方式（"GET" or "POST"）
        :param args : 请求参数
        :param include_agentid : 标识args含有 "agentid" 关键字，需要进行处理
        :returns 返回结果
        """
        shortUrl = urlType[0]
        method = urlType[1]
        response = {}
        for retryCnt in range(0, 3):
            try:
                if "POST" == method:
                    url = self.__makeUrl(shortUrl)
                    if "agentid" in args and include_agentid:
                        url = self.__appendArgs(url, {"agentid": args["agentid"]})
                        del args["agentid"]
                    response = self.__httpPost(url, args)
                elif "GET" == method:
                    url = self.__makeUrl(shortUrl)
                    url = self.__appendArgs(url, args)
                    response = self.__httpGet(url)
                else:
                    raise ApiException(-1, _("unknown method type"))
            except Exception as e:
                raise ApiException(-2, e)  # 其他错误

            # 检查令牌是否过期
            if self.__tokenExpired(response.get("errcode")):
                self.__refreshToken(shortUrl)
                retryCnt += 1
                continue
            else:
                break
        # 检测响应
        return self.__checkResponse(response)

    def httpPostFile(self, urlType, args=None, data=None, headers=None):
        shortUrl = urlType[0]
        response = {}
        for retryCnt in range(0, 3):
            url = self.__makeUrl(shortUrl)
            url = self.__appendArgs(url, args)
            response = self.__httpPostFile(url, data, headers)

            # 检查令牌是否过期
            if self.__tokenExpired(response.get("errcode")):
                self.__refreshToken(shortUrl)
                retryCnt += 1
                continue
            else:
                break
        return self.__checkResponse(response)

    @staticmethod
    def __appendArgs(url, args):
        if args is None:
            return url

        for key, value in args.items():
            if "?" in url:
                url += "&" + key + "=" + value
            else:
                url += "?" + key + "=" + value
        return url

    @staticmethod
    def __makeUrl(shortUrl):
        base = "https://qyapi.weixin.qq.com"
        if shortUrl[0] == "/":
            return base + shortUrl
        else:
            return base + "/" + shortUrl

    def __appendToken(self, url):
        if "SUITE_ACCESS_TOKEN" in url:
            return url.replace("SUITE_ACCESS_TOKEN", self.getSuiteAccessToken())
        elif "PROVIDER_ACCESS_TOKEN" in url:
            return url.replace("PROVIDER_ACCESS_TOKEN", self.getProviderAccessToken())
        elif "ACCESS_TOKEN" in url:
            return url.replace("ACCESS_TOKEN", self.getAccessToken())
        else:
            return url

    def __httpPost(self, url, args):
        realUrl = self.__appendToken(url)

        if self.get_api_debug() is True:
            print("Wecom API POST", realUrl, args)

        return requests.post(
            realUrl, data=json.dumps(args, ensure_ascii=False).encode("utf-8")
        ).json()

    def __httpPostFile(self, url, data, headers):
        realUrl = self.__appendToken(url)

        if self.get_api_debug() is True:
            print("Wecom API POST FILE", realUrl, data, headers)

        # response = requests.post(url=realUrl, data=data, headers=headers).json()
        return requests.post(url=realUrl, data=data, headers=headers).json()

    def __post_file(self, url, media_file):
        if self.get_api_debug() is True:
            print("Wecom API POST FILE", url, media_file)
        return requests.post(url, file=media_file).json()

    def __httpGet(self, url):
        realUrl = self.__appendToken(url)

        if self.get_api_debug() is True:
            print("Wecom API GET", realUrl)

        return requests.get(realUrl).json()

    @staticmethod
    def __checkResponse(response):
        """
        检查 返回 值是否合法，
        """
        errCode = response.get("errcode")
        errMsg = response.get("errmsg")

        if errCode == 0:
            return response
        else:
            raise ApiException(errCode, errMsg)

    @staticmethod
    def __tokenExpired(errCode):
        """
        检查 令牌 是否过期
        """
        if errCode == 40014 or errCode == 42001 or errCode == 42007 or errCode == 42009:
            return True
        else:
            return False

    def __refreshToken(self, url):
        """
        刷新令牌
        """
        if "SUITE_ACCESS_TOKEN" in url:
            self.refreshSuiteAccessToken()
        elif "PROVIDER_ACCESS_TOKEN" in url:
            self.refreshProviderAccessToken()
        elif "ACCESS_TOKEN" in url:
            self.refreshAccessToken()
