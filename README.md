# 企业微信 For Odoo 13.0
odoo 13.0变化很大，发现不少需要改动的。

欢迎提交功能需求

# 适配odoo13.0开发顺序

1. wxwork_contacts （企业微信-通讯簿同步）进行中，计划：
    
    1.1 将企微员工和部门菜单和ODOO HR 菜单合并 ，不再单独显示企微菜单
    
    1.2 同步只针对HR同步，移除“同步向导” 转换employee为user功能
    
    1.3 企微存在一个成员归属多个部门的情况，已向腾讯提交了增加默认部门（首选部门）的需求。
    
    1.4 将企微的设置菜单移到系统设置菜单去，在“用户& 公司”添加子菜单“员工转用户”的功能菜单，在用户窗体中添加“从企业微信更新”按钮
2. wxwork_auth_oauth （企业微信-登录授权）未进行

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