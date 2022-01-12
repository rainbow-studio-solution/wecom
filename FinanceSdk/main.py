from typing import List, Optional, Dict
from fastapi import FastAPI
from pydantic import BaseModel
from sdk.FinanceSdk import FinanceSdk
import logging
_logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

class PrivateKey(BaseModel):
    publickey_ver:int
    private_key:str

class Parameter(BaseModel):
    seq: int
    sdkfileid: str
    corpid: str
    secret: str
    private_keys: Optional[List[PrivateKey]] = None



@app.get("/wecom/finance/get_chatdata")
def get_chatdata(parameter: Parameter):
    sdk = FinanceSdk()
    sdk.init_finance_sdk(parameter.corpid, parameter.secret, parameter.private_keys)
    return sdk.get_chatdata(parameter.seq)

@app.get("/wecom/finance/get_mediadata")
def get_mediadata(parameter: Parameter):
    sdk = FinanceSdk()
    sdk.init_finance_sdk(parameter.corpid, parameter.secret, parameter.private_keys)
    return sdk.get_mediadata(parameter.sdkfileid)