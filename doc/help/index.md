# 帮助

## 错误
1.  Worker (7534) CPU time limit (240) reached. 解决方案/etc/odoo/odoo.conf 添加如下参数：
    ```editorconfig
       ; 将limit_time_cpu修改成合理值
       limit_time_cpu = 600 
    ``` 
2. virtual real time limit (120/120s) reached。 解决方案/etc/odoo/odoo.conf 添加如下参数：
    ```editorconfig
       ; 将limit_time_real修改成合理值
       limit_time_real = 1200
   
## 如何加速Odoo
###  1.参考资料

    标题               | 描述 
    ------------------ | ---------------------------------------------------------
    CPUs               | CPU核心数不是线程数
    Physical           | 物理内存，不是虚拟内存或交换分区
    workers            | 配置文件中指定的worker数（workers = x）
    cron               | Number of workers for cron jobs (max_cron_threads = xx)
    Mem Per            | 以MB为单位的内存，是每个workers请求的最大内存
    Max Mem            | 所有workers可以使用的最大数量
    limit_memory_soft  | 将用于此设置的字节数

    CPUs | Physical | workers | cron | Mem Per | Max Mem | limit_memory_soft  
    ---- | -------- | ------- | ---- | ------- | ------- | -----------------------
    ANY  | =< 256MB |    NR   |  NR  |      NR |     NR  | NR
     1   |   512MB  |    0    |  N/A |     N/A |     N/A | N/A
     1   |   512MB  |    1    |  1   |   177MB |   354MB | 185127901
     1   |    1GB   |    2    |  1   |   244MB |   732MB | 255652815
     1   |    2GB   |    2    |  1   |   506MB |  1518MB | 530242876
     2   |    1GB   |    3    |  1   |   183MB |   732MB | 191739611
     2   |    2GB   |    5    |  2   |   217MB |  1519MB | 227246947
     2   |    4GB   |    5    |  2   |   450MB |  3150MB | 471974428
     4   |    2GB   |    5    |  2   |   217MB |  1519MB | 227246947
     4   |    4GB   |    9    |  2   |   286MB |  3146MB | 300347363
     4   |    8GB   |    9    |  3   |   546MB |  6552MB | 572662306  
     4   |    16GB  |    9    |  3   |  1187MB | 14244MB | 1244918057
 
 
###  2. 依据上述资料进行计算，4核CPU，16G内存的odoo.conf配置如下

```editorconfig
    ; workers = (CPU数量*2) + 1 ，多处理模式仅在基于 unix 的系统上可用
    workers = 9
    max_cron_threads = 3
        
    ;limit_memory_hard = (workers数量+ cron数量)  * 768M * 1024 * 1024(换算成字节)
    limit_memory_hard = 
        
    ;limit-memory-soft = (workers数量+ cron数量) * 1187M * 1024 * 1024(换算成字节)
    limit-memory-soft =
``` 