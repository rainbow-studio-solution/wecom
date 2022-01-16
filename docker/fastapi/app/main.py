# -*- coding: utf-8 -*-

from typing import List, Optional, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from sdk.FinanceSdk import FinanceSdk  # 调试时 使用此引用

# from .sdk.FinanceSdk import FinanceSdk  # build docker 使用此引用

import logging
import base64

_logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


class PrivateKey(BaseModel):
    publickey_ver: int
    private_key: str


class Parameter(BaseModel):
    seq: Optional[int] = Field(
        title="序号"
    )  # 序号，从指定的seq开始拉取消息，注意的是返回的消息从seq+1开始返回，seq为之前接口返回的最大seq值。首次使用请使用seq:0
    sdkfileid: Optional[str] = Field(None, title="消息体内容中的sdkfileid信息")
    proxy: Optional[str] = Field(None, title="代理的链接")
    corpid: Optional[str] = Field(title="企业Id")  # 企业id
    secret: Optional[str] = Field(title="密钥")  # 密钥
    private_keys: Optional[List[PrivateKey]] = Field(None, title="私钥列表")  # 私钥列表


@app.get("/wecom/finance/chatdata")
async def get_chatdata(parameter: Parameter):
    """
    获取聊天数据

    :param parameter:传递参数
    """
    sdk = FinanceSdk()
    sdk.init_finance_sdk(
        parameter.corpid, parameter.secret, parameter.private_keys, parameter.proxy,
    )
    return sdk.get_chatdata(parameter.seq)


@app.get("/wecom/finance/mediadata")
async def get_mediadata(parameter: Parameter):
    """
    获取媒体文件数据

    :param parameter:传递参数
    """
    sdk = FinanceSdk()
    sdk.init_finance_sdk(
        parameter.corpid, parameter.secret, parameter.private_keys, parameter.proxy,
    )
    mediadata = sdk.get_mediadata(parameter.sdkfileid)
    return base64.b64encode(mediadata).decode()
