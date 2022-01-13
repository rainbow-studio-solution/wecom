# 如何使用

## Pull 镜像
```
docker pull rainbowstudiosolution/wecom_fastapi
```

## 启动
```
docker run -d --name wecom_fastapi -p 8000:8000 rainbowstudiosolution/wecom_fastapi
```

## 交互式 API 文档
```
http://127.0.0.1:8000/docs

http://127.0.0.1:8000/redoc
```