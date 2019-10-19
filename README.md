# 企业微信 For Odoo 13.0
odoo 13.0变化很大，发现不少需要改动的。

欢迎提交功能需求

# 适配odoo13.0开发顺序

1. wxwork_contacts （企业微信-通讯簿同步）基本完成，部分需要腾讯更新API，相对12.0变化如下：
    
    1.1 将企微员工和部门菜单和ODOO HR 菜单合并 ，不再单独显示企微菜单    
    1.2 同步只针对HR同步，移除“同步向导” 中转换employee为user功能，批量转换user有点慢。在用户表单头部增加了“复制为系统用户”的按钮,可以单个的转换user     
    1.3 已腾讯提交API增加leader_userid字段，可以直接通过API同步员工的上级人员。 
    1.4 企微存在一个成员归属多个部门的情况，已向腾讯提交了增加默认部门（首选部门）的需求，目前将JSON数据中department[]第一个值作为默认部门。    
    1.5 将企微的设置菜单移到系统设置菜单去，同时增加配置企业定时任务的菜单
    
2. wxwork_auth_oauth （企业微信-登录授权）开发中

# 帮助

## 安装
1. 下载代码
    ```bash
    git clone git@gitee.com:rainbowstudio/wxwork.git --depth 1 --branch 13.0 --single-branch wxwork 
    ```
2. 切换到 wxwork 目录,安装requirements.txt中的python包
    ```bash
    pip install -r requirements.txt -i https://pypi.doubanio.com/simple
    ```
   
## 模块 介绍 

## 使用说明