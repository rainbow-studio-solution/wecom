# 企业微信 For Odoo 13.0
odoo 13.0变化很大，发现不少需要改动的。

欢迎提交功能需求

# 适配odoo13.0开发顺序

1. wxwork_base （企业微信-基础模块）完成适配

2. wxwork_contacts （企业微信-通讯簿同步）基本完成，部分需要腾讯更新API
        
3. wxwork_auth_oauth （企业微信-登录授权）已完成在服务器上的测试

4. wxwork_attendance (企业微信-打卡) 进行中

5. wxwork_notice（企业微信-通知），未开展

6. wxwork_approval（企业微信-审批），未开展

7. wxwork_reset_password（企业微信-密码重置），未开展

# 帮助

## 安装
1. 下载代码
    ```bash
    git clone git@gitee.com:rainbowstudio/wxwork.git --depth 1 --branch 13.0 --single-branch wxwork 
    ```
2. 切换到 wxwork 目录,安装requirements.txt中的python包
    ```bash
    pip install -r requirements.txt -i https://pypi.doubanio.com/simple
   或
   pip3 install -r requirements.txt -i https://pypi.doubanio.com/simple
    ```
 3. 切换到  wxwork/wxwork_api 目录，安装企业微信的API 依赖包
     ```bash
    python setup.py install
    ```
    有空打包上传到 PyPi，暂时先在windows下开发
 
## 模块 介绍 

## 使用说明



如果我的作品能对您有所帮助，能力范围内，请不要介意点击下面“捐赠”按钮。