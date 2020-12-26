<!-- [![Help](http://img.shields.io/badge/14.0-帮助-4cb648.svg?style=flat&colorA=8F8F8F)](doc/help/index.md)
[![Install](http://img.shields.io/badge/14.0-安装-875A7B.svg?style=flat&colorA=8F8F8F)](doc/install/index.md) -->



**请务必阅读安装说明**


_使用过程中发现错误，请参考帮助_

# 企业微信 For Odoo 14.0


自己不是专职开发,还要负债运维和管理,往往一个功能断断续续做出来,要花不少时间.所以请见谅项目的进展速度.

欢迎提交功能需求


## 开源项目 

1. wxwork_l10n （企业微信-本地化模块）
   
2. wxwork_base （企业微信-基础模块）测试通过

3. wxwrok_organization （企业微信-组织架构[部门/员工/用户]模型字段）
   ```
   说明：同步功能死活无法读取新增的模型字段，
   发现模型字段不能含 translate=True
   这🐕东西卡了一个多礼拜
   弄得最后单独将将企业微信有关组织架构的字段单独一个模块处理
   ``` 

4. wxwork_hr_syncing （企业微信-同步功能）开展中......
    ```bash
    #1. 安装扩展
    pip install numpy==1.19.3 opencv-python

    #2. "获取部门成员"API department字段 没有将主部门 默认排第一个，导致同步时设置主部门错误。
    看了下读取成员API，多了个"main_department"（主部门）的字段。已向腾讯企业微信团队提交了需求，
    要么在"获取部门成员"API增加"main_department"（主部门）的字段,要么修复"department"字段的排序。
    设置主部门错误待腾讯修复。
    ``` 

   




# 帮助

## 安装

[![Install](http://img.shields.io/badge/13.0-安装-875A7B.svg?style=flat&colorA=8F8F8F)](doc/install/index.md)

## 故障处理

[![Help](http://img.shields.io/badge/13.0-帮助-4cb648.svg?style=flat&colorA=8F8F8F)](doc/help/index.md)

## 模块 介绍 

## 使用说明

# QQ群

>若有使用问题，可以加入QQ群，寻求本人帮助

![QQ群](doc/img/QQ群二维码.png)

# Odoo商城付费模块

<a href="https://apps.odoo.com/apps/modules/browse?search=RStudio" target="_blank">应用</a>
<a href="https://apps.odoo.com/apps/themes/browse?search=RStudio" target="_blank">主题</a>


如果我的作品能对您有所帮助，能力范围内，请不要介意点击下面“捐赠”按钮，或者点个⭐，开源不易，请多支持。
