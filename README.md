# 企业微信 For Odoo 14.0

```bash
load could not load template
ValueError: 元素 '<xpath expr="//*[hasclass('o_footer_copyright_name')]">' 在母级视图中没有找到

检查是portal一个视图错误，待odoo官方修复
或者在未安装website相关模块下使用sql删除

DELETE FROM  "ir_ui_view" WHERE key='portal.footer_language_selector'

不会写sql的，可以开启debug模式(url地址的web后面增加’?debug=1‘);
打开odoo的设置-技术-用户菜单--视图，搜索：Footer Language Selector，找到外部id为：portal.footer_language_selector
编辑设置有效为False
```

## 项目地址
[![Github](http://img.shields.io/badge/14.0-Github-4cb648.svg?style=flat&colorA=8F8F8F)](https://github.com/rainbow-studio-solution/wxwork)
[![Gitee](http://img.shields.io/badge/14.0-Gitee-875A7B.svg?style=flat&colorA=8F8F8F)](https://gitee.com/rainbowstudio/wxwork)


## 开源项目 

1. wxwork_l10n （企业微信-本地化模块） 完成
   
2. wxwork_base （企业微信-基础模块）完成

3. wxwork_hr （企业微信-HR模块）完成


4. wxwork_hr_syncing （企业微信-同步功能）完成......
    ```bash
    #1. 安装扩展
    pip install numpy==1.19.3 opencv-python==4.4.0.46

    #2. 
    "获取部门成员"API department字段 没有将主部门 默认排第一个，导致同步时设置主部门错误。
    看了下读取成员API，多了个"main_department"（主部门）的字段。已向腾讯企业微信团队提交了需求，
    要么在"获取部门成员"API增加"main_department"（主部门）的字段,要么修复"department"字段的排序。
    设置主部门错误待腾讯修复。
    ``` 
5. wxwork_hr_extension（企业微信-HR扩展模块）完成
   ```
   功能：将Odoo中的所有关于HR的模块菜单，按照实际的业务流程进行整合，进行HR的集中管理
   ``` 
6. wxwork_auth_oauth （企业微信应用内自动登录，企业微信应用外扫码登录），完成
   ```bash
   #若出现链接失败的提示或其他的失败提示，尝试修改odoo.conf 以下参数，我是直接放大10倍
   db_maxconn = 640
   limit_time_cpu = 600
   limit_time_real = 1200 
   ```
7. wxwork_widget（企业微信消息模板markdown编辑器,密码显示等小部件），完成
8. wxwork_message_push（企业微信消息推送），开展中
9.  wxwork_attendance（拉取考勤记录），开展中

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


如果我的作品能对您有所帮助，能力范围内，请不要介意去<a href="https://gitee.com/rainbowstudio/wxwork">Gitee</a>点击“捐赠”按钮，或者点个⭐，一切随意，开源不易，请多支持。
