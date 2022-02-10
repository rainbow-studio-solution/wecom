# 企业微信 For Odoo 15.0


[![Github](http://img.shields.io/badge/Wecom14.0-Github-4cb648.svg?style=flat&colorA=8F8F8F)](https://github.com/rainbow-studio-solution/wecom)
[![Gitee](http://img.shields.io/badge/Wecom14.0-Gitee-875A7B.svg?style=flat&colorA=8F8F8F)](https://gitee.com/rainbowstudio/wecom)
[![Docker](http://img.shields.io/badge/Wecom14.0-Docker-C22D40.svg?style=flat&colorA=8F8F8F)](https://hub.docker.com/r/rainbowstudiosolution/wecom_for_odoo)
[![Docs](http://img.shields.io/badge/Wecom14.0-Docs-F34B7D.svg?style=flat&colorA=8F8F8F)](https://docs.rstudio.xyz/zh/14.0/wecom)
[![SDK](http://img.shields.io/badge/企微SDK-API-F34B7D.svg?style=flat&colorA=8F8F8F)](https://gitee.com/rainbowstudio/wecom_sdk_service/)


## 功能模块介绍

> 在14.0的基础上， 将通讯簿应用从wecom_base剥离, 并将通讯簿模块放到wecom_contacts中，取消了 wecom_hrm_syncing 模块，同步功能模块放到wecom_contacts_sync中。

1. wecom_api 企微API，封装 企业微信服务端API和客户端API，完成。
2. wecom_l10n 企微本地化，用于模块本地化，完成。
3. wecom_widget 企微小部件，部分需要适配15.0，暂时不影响使用，回头处理。
4. wecom_base  企微基础，功能：企微应用，应用参数，应用事件，应用类型，Odoo相关模型添加企业微信字段，完成。
5. wecom_contacts 企微联系人，企业微信通讯录应用，完成。
6. wecom_contacts_sync 企微联系人同步，完成：企微通讯簿向导同步，事件同步，待完成功能：自动任务同步。
7. wecom_hrm 企微HRM 管理企业微信的部门、成员和标签，整合和重建odoo Hr的菜单。待完成生成系统用户功能。
8. wecom_hrm_extension 企微HRM扩展，安装Odoo中所有Hr相关的模块，整合和重建odoo Hr的菜单。未完成。
9. wecom_material 企微媒体素材，用于资源文件，一次上传可以多次使用，完成。
10. wecom_message 企业微信，拦截标识为企业微信用户目标对象的电子邮件，通过企业微信向目标对象推送文本、图片、视频、文件、图形等类型的消息。待处理
11. wecom_digest_message 企微摘要邮件消息模块，未完成。
12. wecom_portal 企微门户，未完成。
13. wecom_msgaudit 企微会话存档，企业可通过接口获取成员会话内容，以符合企业监管合规要求和保障客户服务质量，未完成。
14. ......



# QQ群

>若有使用问题，可以加入QQ群，寻求本人帮助

![QQ群](doc/img/QQ群二维码.png)

# Odoo商城付费模块

<a href="https://apps.odoo.com/apps/modules/browse?search=RStudio" target="_blank">应用</a>
<a href="https://apps.odoo.com/apps/themes/browse?search=RStudio" target="_blank">主题</a>


如果我的作品能对您有所帮助，能力范围内，请不要介意去<a href="https://gitee.com/rainbowstudio/wxwork">Gitee</a>点击“捐赠”按钮，或者点个⭐，一切随意，开源不易，请多支持。
