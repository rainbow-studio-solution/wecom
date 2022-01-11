# -*- coding: utf-8 -*-

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException


class FinanceSdkInitException(ApiException):
    pass


class FinanceSdkGetChatDataException(ApiException):
    pass


class FinanceSdkDecryptException(ApiException):
    pass


class FinanceSdkGetMediaDataException(ApiException):
    pass
