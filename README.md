# 企业微信 For Odoo 15.0


[![Github](http://img.shields.io/badge/Wecom15.0-Github-4cb648.svg?style=flat&colorA=8F8F8F)](https://github.com/rainbow-studio-solution/wecom)
[![Gitee](http://img.shields.io/badge/Wecom15.0-Gitee-875A7B.svg?style=flat&colorA=8F8F8F)](https://gitee.com/rainbowstudio/wecom)
[![Docker](http://img.shields.io/badge/Wecom15.0-Docker-C22D40.svg?style=flat&colorA=8F8F8F)](https://hub.docker.com/r/rainbowstudiosolution/wecom_for_odoo)
[![Docs](http://img.shields.io/badge/Wecom15.0-Docs-F34B7D.svg?style=flat&colorA=8F8F8F)](https://docs.rstudio.xyz/zh/14.0/wecom)
[![SDK](http://img.shields.io/badge/企微SDK-API-F34B7D.svg?style=flat&colorA=8F8F8F)](https://gitee.com/rainbowstudio/wecom_sdk_service/)


## 功能模块介绍

> 在14.0的基础上， 将通讯簿应用从wecom_base剥离, 并将通讯簿模块放到wecom_contacts中，取消了 hrmis_syncing 模块，同步功能模块放到wecom_contacts_sync中。
> 尚未开发完成，暂时不要使用
> 
|   #   | 模块名称            | 模块介绍                                                                               | 开源  | 状态  |
| :---: | :------------------ | :------------------------------------------------------------------------------------- | :---: | :---: |
|   1   | wecom_api           | 企微API，企微API错误代码，封装 企业微信服务端API和客户端API                            |   ✔   |   ✔   |
|   2   | wecom_l10n          | 企微本地化，用于模块本地化                                                             |   ✔   |   ✔   |
|   3   | wecom_widget        | 企微小部件                                                                             |   ✔   |   ✔   |
|   4   | wecom_base          | 企微基础，功能：企微应用，应用参数，应用事件，应用类型，Odoo相关模型添加企业微信字段   |   ✔   |   ✔   |
|   5   | wecom_contacts      | 企微联系人，企业微信通讯录应用                                                         |   ✔   |   ✔   |
|   6   | wecom_material      | 企微媒体素材，用于资源文件，一次上传可以多次使用                                       |   ✔   |   ✔   |
|   7   | wecom_auth_oauth    | 网页扫码登陆，企业客户端内置浏览器一键登陆                                             |   ✔   |   ✔   |
|   8   | wecom_contacts_sync | 企微联系人同步，完成：企微通讯簿向导同步，事件同步                                     |   ✔   |   ✔   |
|   9   | wecom_portal        | 企微门户，企微应用的菜单设置                                                           |   ✔   | ..... |
|  10   | hrmis               | 人力资源管理信息系统 管理企业微信的部门、成员和标签，整合和重建odoo Hr的菜单           |   ✔   |   ✔   |
|  11   | hrmis_extension     | 人力资源管理信息系统 扩展，安装Odoo中所有Hr相关的模块，整合和重建odoo Hr的菜单。       |   ✔   |   ✖   |
|  12   | wecom_checkin       | 企微打卡，获取企微的打卡数据及相关分析报表                                             |   ✔   |   ✖   |
|  13   | wecom_attendance    | 企微考勤排班                                                                           |   ✖   |   ✖   |
|  13   | wecom_hr_appraisal  | 企微员工评价，适用于服务行业，客人扫码员工胸前的个人二维码，对其进行评价和金额打赏     |   ✖   |   ✖   |
|  14   | wecom_wedrive       | 企微微盘基础                                                                           |   ✔   |   ✖   |
|  15   | wecom_msgaudit      | 企微会话存档，企业可通过接口获取成员会话内容，以符合企业监管合规要求和保障客户服务质量 |   ✔   |   ✖   |
|  16   | wecom_web_theme     | 企微专用的Odoo Web后端主题，提供后台网页响应式能力。便于在使用移动终端的企业微信应用中访问Odoo      |   ✖   | ✔  |
|  17   | wecom_approval      | 企微审批，同步企业微信审批。完成审批后执行对应的odoo模型动作                           |   ✖   |   ✖   |
|  18   | wecom_calendar      | 企微日历，odoo与企微的日历双向同步                                                     |   ✖   |   ✖   |
|  19   | wecom_pay           | 企微支付                                                                               |   ✖   |   ✖   |

> 状态说明：
> 
| 状态符号 |  说明  |
| :------: | :----: |
|    ✔     | 已完成 |
|  .....   | 进行中 |
|    ✖     | 未开始 |

# QQ群

>若有使用问题，可以加入QQ群，寻求本人帮助

![QQ群](doc/img/QQ群二维码.png)

# Odoo商城付费模块

<a href="https://apps.odoo.com/apps/modules/browse?search=RStudio" target="_blank">应用</a>
<a href="https://apps.odoo.com/apps/themes/browse?search=RStudio" target="_blank">主题</a>


如果我的作品能对您有所帮助，能力范围内，请不要介意去<a href="https://gitee.com/rainbowstudio/wecom">Gitee</a>点击“捐赠”按钮，或者点个⭐，一切随意，开源不易，请多支持。
