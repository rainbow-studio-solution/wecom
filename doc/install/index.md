## 安装

1. 下载代码
   ```bash
   git clone https://gitee.com/rainbowstudio/wecom.git --depth 1 --branch 14.0 --single-branch wxwork
   ```
2. 切换到 wxwork 目录,安装 requirements.txt 中的 python 包
   ```bash
   pip install -r requirements.txt -i https://pypi.doubanio.com/simple
   或
   pip3 install -r requirements.txt -i https://pypi.doubanio.com/simple
   ```
3. 将 wxwork 目录添加到 odoo 的配置文件:

```
vi /etc/odoo/odoo.conf

将addons_path修改为:
addons_path = /your/wxwork,/usr/lib/python3/dist-packages/odoo/addons

```

4. 重启 odoo:

```
systemctl restart odoo
```

5. 激活并安装 wxwork
   如果在后台应用列表没有看到 wxwork，需进入 odoo 的 debug 模式刷新本地模块

```
https://yourodoo/web?debug=1
```

FAQ:

1. 重启 odoo 后进入应用安装页面是空白
   A:建议先查看 odoo 的日志，一般来说可能是你给 wxwork 的权限不对。
