# 企业微信SDK 服务

## 用途（暂时只有2个）

1. 用于获取企业微信会话内容存档的聊天记录
2. 用于获取企业微信会话内容存档的聊天记录中的媒体文件

# 为什么使用FastAPI，而不是直接在Odoo中直接调用
1. 社区朋友的测试结果，目前社区朋友已经这个问题提交给了odoo，[链接](https://github.com/odoo/odoo/issues/82623)：
    ```
    odoo addons，依赖了多个三方库，这些库里面的某个用了（非pytyhon）c++库；它用的gcc/libstdc++ 库版本，和企业微信sdk提供的sdk.so编译使用的 gcc/libstdc++库不兼容。
    因为odoo addons机制先把这个依赖库(它用的gcc/libstdc++）加载了，然后才加载的 ctypes.CDLL(sdk_lib_path), 所以导致这里加载so时coredump了.
    ```
2. 经过2周的时间，也无法解决odoo加载c++库崩溃的问题，我已经崩溃了，干脆使用FastAPI封装企业微信会话内部存档的SDK，让Odoo访问 FastAPI,获取到相关信息。



## 安装依赖
> 切换到 wecom_sdk 路径
```
pip3 install "uvicorn[standard]" -i https://pypi.doubanio.com/simple 
pip3 install fastapi pydantic pycryptodome -i https://pypi.doubanio.com/simple 
```

## 添加wecomsdk服务
1. 添加 wecomsdk.service 文件到 /lib/systemd/system/
2. 在 /lib/systemd/system/ecomsdk.service 中添加以下内容：
```
[Unit]
Description=Wecom Sdk Api
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
ExecStart=/usr/bin/python3  /code/app/main.py
StandardOutput=file:/var/log/wecom/wecom-server.log
StandardInput=tty-force
# Restart=always

[Install]
WantedBy=multi-user.target
```
3. 启动服务
```
systemctl enable wecomsdk
systemctl start wecomsdk
```

4. 查看日志
```
tail -f /var/log/wecom/wecom-server.log
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

    ir_config = self.env["ir.config_parameter"].sudo()
    chatdata_url = ir_config.get_param(
        "wecom.msgaudit.msgaudit_sdk_url"
    ) + ir_config.get_param("wecom.msgaudit.msgaudit_chatdata_url")

    proxy = (
        True
        if ir_config.get_param("wecom.msgaudit_sdk_proxy") == "True"
        else False
    )

    headers = {"content-type": "application/json"}
    body = {
        "seq": max_seq_id, #从指定的seq开始拉取消息，注意的是返回的消息从seq+1开始返回，seq为之前接口返回的最大seq值。首次使用请使用seq:0
        "corpid": corpid,
        "secret": secret,
        "private_keys": 私钥列表,
    }
    if proxy:
        body.update(
            {"proxy": chatdata_url, "paswd": "odoo:odoo",}
        )
    r = requests.get(chatdata_url, data=json.dumps(body), headers=headers)
    chat_datas = r.json()
   ```
2. 获取媒体文件
   ```
    import requests
    import json

    ir_config = self.env["ir.config_parameter"].sudo()
    mediadata_url = ir_config.get_param(
        "wecom.msgaudit.msgaudit_sdk_url"
    ) + ir_config.get_param("wecom.msgaudit.msgaudit_mediadata_url")
    proxy = (
        True
        if ir_config.get_param("wecom.msgaudit_sdk_proxy") == "True"
        else False
    )

    headers = {"content-type": "application/json"}
    body = {
        "seq": 0, #为0即可
        "sdkfileid": 消息体内容中的sdkfileid信息,
        "corpid": corpid,
        "secret": secret,
        "private_keys": 私钥列表,
    }
    if proxy:
        body.update(
            {"proxy": mediadata_url, "paswd": "odoo:odoo",}
        )
    r = requests.get(mediadata_url, data=json.dumps(body), headers=headers)
    mediadata = r.json()
   ```

# SDK错误码说明 
| 返回值 | 说明           | 建议                                                                                                                                    |
| :----- | :------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| 10000  | 请求参数错误   | 检查Init接口corpid、secret参数；检查GetChatData接口limit参数是否未填或大于1000；检查GetMediaData接口sdkfileid是否为空，indexbuf是否正常 |
| 10001  | 网络请求错误   | 检查是否网络有异常、波动；检查使用代理的情况下代理参数是否设置正确的用户名与密码                                                        |
| 10002  | 数据解析失败   | 建议重试请求。若仍失败，可以反馈给企业微信进行查询，请提供sdk接口参数与调用时间点等信息                                                 |
| 10003  | 系统调用失败   | GetMediaData调用失败，建议重试请求。若仍失败，可以反馈给企业微信进行查询，请提供sdk接口参数与调用时间点等信息                           |
| 10004  | 已废弃         | 目前不会返回此错误码                                                                                                                    |
| 10005  | fileid错误     | 检查在GetMediaData接口传入的sdkfileid是否正确                                                                                           |
| 10006  | 解密失败       | 请检查是否先进行base64decode再进行rsa私钥解密，再进行DecryptMsg调用                                                                     |
| 10007  | 已废弃         | 目前不会返回此错误码                                                                                                                    |
| 10008  | DecryptMsg错误 | 建议重试请求。若仍失败，可以反馈给企业微信进行查询，请提供sdk接口参数与调用时间点等信息                                                 |
| 10009  | ip非法         | 请检查sdk访问外网的ip是否与管理端设置的可信ip匹配，若不匹配会返回此错误码                                                               |
| 10010  | 请求的数据过期 | 用户欲拉取的数据已过期，仅支持近3天内的数据拉取                                                                                         |
| 10011  | ssl证书错误    | 使用openssl版本sdk，校验ssl证书失败                                                                                                     |