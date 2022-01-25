# -*- coding: utf-8 -*-

import uvicorn
import sys
import traceback

# Configuration File
import config as cfg


from typing import List, Optional, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


from sdk.FinanceSdk import FinanceSdk  # 调试时 使用此引用

# from .sdk.FinanceSdk import FinanceSdk  # build docker 使用此引用

import logging
import base64

_logger = logging.getLogger(__name__)

######################
# Fast API
######################
app = FastAPI(
    title="企业微信SKD API",
    description="""
    功能：\n
    1.获取会话内容存档的的聊天记录；
    2.解析聊天记录中的媒体文件。
    """,
    version="1.0",
)


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
    paswd: Optional[str] = Field(None, title="代理账号密码")
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
        parameter.corpid,
        parameter.secret,
        parameter.private_keys,
        parameter.proxy,
        parameter.paswd,
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
        parameter.corpid,
        parameter.secret,
        parameter.private_keys,
        parameter.proxy,
        parameter.paswd,
    )
    mediadata = sdk.get_mediadata(parameter.sdkfileid)
    return base64.b64encode(mediadata).decode()


if __name__ == "__main__":
    print(f'Starting API Server: {cfg.config["host"]}:{cfg.config["port"]}\n')

    try:
        uvicorn.run(
            "main:app",
            host=cfg.config["host"],
            port=cfg.config["port"],
            workers=cfg.config["workers"],
            log_level=cfg.config["log_level"],
            reload=cfg.config["reload"],
            debug=cfg.config["debug"],
        )
    except KeyboardInterrupt:
        print(f"\nExiting\n")
    except Exception as e:
        print(f"Failed to Start API")
        print("=" * 100)
        traceback.print_exc(file=sys.stdout)
        print("=" * 100)
        print("Exiting\n")
    print(f"\n\n")

