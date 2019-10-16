# 企业微信 For Odoo 13.0
odoo 13.0变化很大，发现不少需要改动的

# 适配odoo13.0开发顺序

1. wxwork_contacts （企业微信-通讯簿同步）进行中
2. wxwork_auth_oauth （企业微信-登录授权）未进行

# 安装说明
1. 下载代码
    ```bash
    git clone git@gitee.com:rainbowstudio/wxwork.git --depth 1 --branch 13.0 --single-branch wxwork 
    ```
2. 切换到 wxwork 目录,安装requirements.txt中的python包
    ```bash
    pip install -r requirements.txt -i https://pypi.doubanio.com/simple
    ```