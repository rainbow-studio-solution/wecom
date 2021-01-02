# 企业微信 For Odoo 14.0

## 项目地址
[![Github](http://img.shields.io/badge/14.0-Github-4cb648.svg?style=flat&colorA=8F8F8F)](https://github.com/rainbow-studio-solution/wxwork)
[![Gitee](http://img.shields.io/badge/14.0-Gitee-875A7B.svg?style=flat&colorA=8F8F8F)](https://gitee.com/rainbowstudio/wxwork)


## 开源项目 

1. wxwork_l10n （企业微信-本地化模块） 完成
   
2. wxwork_base （企业微信-基础模块）完成

3. wxwrok_organization （企业微信-组织架构[部门/员工/用户]模型字段）完成
   ```
   说明：同步功能死活无法读取新增的模型字段，
   发现模型字段不能含 translate=True
   这🐕东西卡了一个多礼拜
   弄得最后单独将将企业微信有关组织架构的字段单独一个模块处理
   ``` 

4. wxwork_hr_syncing （企业微信-同步功能）完成......
    ```bash
    #1. 安装扩展
    pip install numpy==1.19.3 opencv-python

    #2. 
    "获取部门成员"API department字段 没有将主部门 默认排第一个，导致同步时设置主部门错误。
    看了下读取成员API，多了个"main_department"（主部门）的字段。已向腾讯企业微信团队提交了需求，
    要么在"获取部门成员"API增加"main_department"（主部门）的字段,要么修复"department"字段的排序。
    设置主部门错误待腾讯修复。
    ``` 
5. wxwork_auth_oauth （企业微信应用内自动登录，企业微信应用外扫码登录），完成
   ```bash
   #若出现链接失败的提示或其他的失败提示，尝试修改odoo.conf 以下参数，我是直接放大10倍
   db_maxconn = 640
   limit_time_cpu = 600
   limit_time_real = 1200 
   ```
6. wxwork_markdown_editor（企业微信消息模板markdown编辑器），开展中
7. wxwork_message_push（企业微信消息推送），开展中
8. 拉取考勤记录

## 闭源项目


# 功能模块列表

# 帮助

## 安装

[![Install](http://img.shields.io/badge/14.0-安装-875A7B.svg?style=flat&colorA=8F8F8F)](doc/install/index.md)

## 故障处理

[![Help](http://img.shields.io/badge/14.0-帮助-4cb648.svg?style=flat&colorA=8F8F8F)](doc/help/index.md)



# QQ群

>若有使用问题，可以加入QQ群，寻求本人帮助

![QQ群](doc/img/QQ群二维码.png)

# Odoo商城付费模块

<a href="https://apps.odoo.com/apps/modules/browse?search=RStudio" target="_blank">应用</a>
<a href="https://apps.odoo.com/apps/themes/browse?search=RStudio" target="_blank">主题</a>


如果我的作品能对您有所帮助，能力范围内，请不要介意点击下面“捐赠”按钮，或者点个⭐，开源不易，请多支持。
