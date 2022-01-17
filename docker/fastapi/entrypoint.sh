#!/bin/bash

#  启动 squid
# service squid restart

 # 启动fastapi
# systemctl restart wecomsdk
#  python3 uvicorn app.main:app --host 0.0.0.0 --port 8000

# tinyproxy -c /etc/tinyproxy/tinyproxy.conf
service tinyproxy start 