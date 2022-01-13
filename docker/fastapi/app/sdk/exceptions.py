# -*- coding: utf-8 -*-
class WecomException(Exception):
    code = 0
    message = ""

    def __init__(self, code, message):
        self.code = code
        self.message = message


class FinanceSdkInitException(WecomException):
    pass


class FinanceSdkGetChatDataException(WecomException):
    pass


class FinanceSdkDecryptException(WecomException):
    pass


class FinanceSdkGetMediaDataException(WecomException):
    pass
