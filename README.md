# 企业微信 For Odoo 14.0

[![Github](http://img.shields.io/badge/14.0-Github-4cb648.svg?style=flat&colorA=8F8F8F)](https://github.com/rainbow-studio-solution/wecom)
[![Gitee](http://img.shields.io/badge/14.0-Gitee-875A7B.svg?style=flat&colorA=8F8F8F)](https://gitee.com/rainbowstudio/wecom)
[![Docker](http://img.shields.io/badge/Wecom_For_Odoo-Docker-C22D40.svg?style=flat&colorA=8F8F8F)](https://hub.docker.com/r/rainbowstudiosolution/wecom_for_odoo)
[![Docker](http://img.shields.io/badge/FastAPI-Docker-F34B7D.svg?style=flat&colorA=8F8F8F)](https://hub.docker.com/r/rainbowstudiosolution/wecom_fastapi)


**2021/12/01 基本可以用，请下载发行版的第二个版本**

**准备重构下 API 模块，不然不利于企业微信的接收消息回调功能，请暂时不用使用 GIT**

> 以下功能是开源版本准备添加的：

- 应用列表：对应企业微信后台的应用
- 应用参数：多对一关联到应用列表
- 应用事件：
  - 事件服务：多对一关联到应用列表
  - 事件类型：存储事件关联的模型、事件类型、事件需要执行的代码和指令
- 应用类型
  - 应用类型：对应企业微信，设置了 4 个类型：管理工具、基础应用、自建应用、第三方应用
  - 子类型：多对一关联到应用类型，用于视图显示 以及 传参用途

> 完成以上功能后（企微消息和企微员工门户暂时延后），照客户的需求开发收费版本的会话存档功能先。

## 项目地址

## 功能模块介绍

### 基础模块

| 模块名称               | 功能介绍                                                                                                                                            | 是否收费 | 完工状态 |
| :--------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | -------: | -------: |
| wecom_l10n             | 语言本地化                                                                                                                                          |       否 |   `完成` |
| wecom_widget           | 企业微信小部件，含（json 编辑器，Markdown 编辑器，密码显示等）                                                                                      |       否 |   `完成` |
| wecom_base             | 基础模块                                                                                                                                            |       否 |   `完成` |
| wecom_api              | 企微服务端 API 和客户端 API                                                                                                                         |       否 |   `完成` |
| wecom_api              | 企微服务端 API 和客户端 API                                                                                                                         |       否 |   `完成` |
| web_widget_colorpicker | 采色器，来源 `<a href="https://apps.odoo.com/apps/modules/14.0/web_widget_colorpicker/" target="_blank">`Web Widget Colorpicker `</a>`,做了部分修改 |       否 |   `完成` |

### 企业微信增强功能

| 模块名称       | 功能介绍     | 是否收费 |         完工状态 |
| :------------- | ------------ | -------: | ---------------: |
| wecom_material | 企微媒体素材 |       否 |           `完成` |
| wecom_message  | 企微消息     |       否 | 完成模板发送消息 |

### 门户

| 模块名称     | 功能介绍     | 是否收费 |                           完工状态 |
| :----------- | ------------ | -------: | ---------------------------------: |
| wecom_portal | 企微员工门户 |       否 | 暂时增加了在个人门户显示企微二维码 |

### 验证登陆

| 模块名称         | 功能介绍                                     | 是否收费 | 完工状态 |
| :--------------- | -------------------------------------------- | -------: | -------: |
| wecom_auth_oauth | 企微内置浏览器一键登陆和第三方浏览器扫码登陆 |       否 |   `完成` |

### HRM

| 模块名称            | 功能介绍                                                   | 是否收费 | 完工状态 |
| :------------------ | ---------------------------------------------------------- | -------: | -------: |
| wecom_hrm           | 企微 HRM，                                                 |       否 |   `完成` |
| wecom_hrm_syncing   | 企微 HRM 同步，同步企业微信的部门、人员、标签到 Odoo 的 HR |       否 |   `完成` |
| wecom_hrm_extension | 企微 HRM 扩展                                              |       否 |       `` |

# 帮助

## 安装

## 故障处理

## CentOS 问题

# QQ 群

> 若有使用问题，可以加入 QQ 群，寻求本人帮助

![QQ群](doc/img/QQ群二维码.png)

# Odoo 商城付费模块

<a href="https://apps.odoo.com/apps/modules/browse?search=RStudio" target="_blank">应用</a>
<a href="https://apps.odoo.com/apps/themes/browse?search=RStudio" target="_blank">主题</a>

如果我的作品能对您有所帮助，能力范围内，请不要介意去 `<a href="https://gitee.com/rainbowstudio/wecom">`Gitee `</a>`点击“捐赠”按钮，或者点个 ⭐，一切随意，开源不易，请多支持。
