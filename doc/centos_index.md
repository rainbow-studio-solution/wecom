# 帮助
## 在linux上查看实时日志
使用以下命令实时查看odoo运行日志：
```editorconfig
tail -f /var/log/odoo/odoo-server.log 
``` 

## 错误
1.  ImportError: libGL.so.1: cannot open shared object file: No such file or directory. 
    解决方案 安装mesa-libGL.x86_64：
    ```editorconfig
       yum install mesa-libGL.x86_64
    ``` 