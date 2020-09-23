[![Help](http://img.shields.io/badge/13.0-帮助-4cb648.svg?style=flat&colorA=8F8F8F)](doc/help/index.md)
[![Install](http://img.shields.io/badge/13.0-安装-875A7B.svg?style=flat&colorA=8F8F8F)](doc/install/index.md)

**请务必阅读安装说明**

**目前 同步通讯录和验证登陆可以正常使用了**  
_使用过程中发现错误，请参考帮助_

# 企业微信 For Odoo 13.0

odoo 13.0变化很大，发现不少需要改动的。

自己不是专职开发,还要负债运维和管理,往往一个功能断断续续做出来,要花不少时间.所以请见谅项目的进展速度.

欢迎提交功能需求

# 适配odoo13.0开发计划，随着自己的想法而变动

## 开源项目 (2020-09-14)

1. wxwork_base （企业微信-基础模块）完成适配
2. wxwork_users_syncing （企业微信-用户同步，原名 wxwork_contacts）完成
3. wxwork_auth_oauth （企业微信-登录授权）,初步完成。PC版本企业微信内置浏览器访问Odoo的白屏问题待解决。
   
    企业微信的内置浏览器是什么:
    1. ios企业微信用的ios系统自带的WKWebview
    2. Android的是tbs x5
    3. mac版的微信浏览器内核是系统的safari
    4. windows版cef核心浏览器版本是Chromium框架53
   
    测试发现，在Android手机端的企业微信可以使用内置浏览器一键登录Odoo，PC版本反而不行，Chromium框架53估计太老了，Odoo的js一些新特性无法运行，导致在PC版的企业微信上打开Odoo的登录页面白屏。

5. wxwork_markdown_editor(Markdonw编辑器企业微信专用版)
4. wxwork_message_push（企业微信消息推送，原名wxwork_notice），开展中




# 帮助

## 安装

[![Install](http://img.shields.io/badge/13.0-安装-875A7B.svg?style=flat&colorA=8F8F8F)](doc/install/index.md)

## 故障处理

[![Help](http://img.shields.io/badge/13.0-帮助-4cb648.svg?style=flat&colorA=8F8F8F)](doc/help/index.md)

## 模块 介绍 

## 使用说明

## QQ群

>若有使用问题，可以加入QQ群，寻求本人帮助

![QQ群](doc/img/QQ群二维码.png)

## Odoo商城付费模块

<a href="https://apps.odoo.com/apps/modules/browse?search=RStudio" target="_blank">应用</a>
<a href="https://apps.odoo.com/apps/themes/browse?search=RStudio" target="_blank">主题</a>


如果我的作品能对您有所帮助，能力范围内，请不要介意点击下面“捐赠”按钮，或者点个⭐。
