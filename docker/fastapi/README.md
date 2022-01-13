# 用途（暂时只有2个）

1. 用于获取企业微信会话内容存档的聊天记录
2. 用于获取企业微信会话内容存档的聊天记录中的媒体文件

# 为什么使用FastAPI，而不是直接在Odoo中直接调用
1. 社区朋友的测试结果，目前社区朋友已经这个问题提交给了odoo，[链接](https://github.com/odoo/odoo/issues/82623)：
    ```
    odoo addons，依赖了多个三方库，这些库里面的某个用了（非pytyhon）c++库；它用的gcc/libstdc++ 库版本，和企业微信sdk提供的sdk.so编译使用的 gcc/libstdc++库不兼容。
    因为odoo addons机制先把这个依赖库(它用的gcc/libstdc++）加载了，然后才加载的 ctypes.CDLL(sdk_lib_path), 所以导致这里加载so时coredump了.
    ```
2. 经过2周的时间，也无法解决odoo加载c++库崩溃的问题，我已经崩溃了，干脆使用FastAPI封装企业微信会话内部存档的SDK，让Odoo访问 FastAPI,获取到相关信息。



# 如何使用

## Pull 镜像
```
docker pull rainbowstudiosolution/wecom_fastapi
```

## 启动
```
docker run -d --name wecom_fastapi -p 8000:8000 -t rainbowstudiosolution/wecom_fastapi
```

## 交互式 API 文档
```
http://127.0.0.1:8000/docs

http://127.0.0.1:8000/redoc
```

# 请求示例

> 代码示例路径：  \wecom_msgaudit\models\wecom_chatdata.py

1. 获取聊天记录
   ```
    import requests
    import json

    chatdata_api_url = "http://localhost:8000/wecom/finance/chatdata"

    headers = {"content-type": "application/json"}
    body = {
        "seq": max_seq_id, #从指定的seq开始拉取消息，注意的是返回的消息从seq+1开始返回，seq为之前接口返回的最大seq值。首次使用请使用seq:0
        "corpid": corpid,
        "secret": secret,
        "private_keys": 私钥列表,
    }
    r = requests.get(chatdata_api_url, data=json.dumps(body), headers=headers)
    chat_datas = r.json()
   ```
2. 获取媒体文件
   ```
    import requests
    import json

    mediadata_api_url = "http://localhost:8000/wecom/finance/mediadata"

    headers = {"content-type": "application/json"}
    body = {
        "seq": 0, #为0即可
        "sdkfileid": 消息体内容中的sdkfileid信息,
        "corpid": corpid,
        "secret": secret,
        "private_keys": 私钥列表,
    }
    r = requests.get(mediadata_api_url, data=json.dumps(body), headers=headers)
    chat_datas = r.json()
   ```