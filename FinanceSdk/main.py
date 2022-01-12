from typing import Optional, Text
from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    corpid: str
    secret: str
    private_keys: List[private]

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/wecom/finance/get_chatdata")
async def get_chatdata(item:Item):
    # corpid, secret, private_keys
    return item