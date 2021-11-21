# 帮助
## 在linux上查看实时日志
使用以下命令实时查看odoo运行日志：
```editorconfig
tail -f /var/log/odoo/odoo-server.log 
``` 

## 错误
1.  Worker (7534) CPU time limit (240) reached. 解决方案/etc/odoo/odoo.conf 添加如下参数：
    ```editorconfig
       ; 将limit_time_cpu修改成合适的值
       limit_time_cpu = 600 
    ``` 
2. virtual real time limit (120/120s) reached。 解决方案/etc/odoo/odoo.conf 添加如下参数：
    ```editorconfig
       ; 将limit_time_real修改成合适的值
       limit_time_real = 1200
    ``` 
3. PoolError('The Connection Pool Is Full')。 解决方案/etc/odoo/odoo.conf 添加如下参数：  
    ```editorconfig
       ; 将db_maxconn修改成合适的值
       db_maxconn = 1200
    ``` 

## 如何加速Odoo
###  1.参考资料
    
    Odoo包含内置的HTTP服务器，使用多线程或多处理。  
    
    对于生产用途，建议使用多处理服务器，因为它可以提高稳定性，更好地利用计算资源，并且可以更好地监控和限制资源。  
    
    workers数量应基于计算机中的核心数量（可能为cron worker提供一些空间，具体取决于预测的cron工作量）
    
    可以根据硬件配置工作器限制配置以避免资源耗尽警告  
    
    注意： Windows上目前无法使用多处理模式
    
#### 配置

* 每个可用CPU应使用2个工作线程+ 1个cron线程，每10个concurent用户使用1个CPU。确保调整配置文件中的内存限制和CPU限制。
    ```editorconfig
       workers = --workers <count>
    ```   
* 如果count不为0（默认值），则启用多处理并设置指定数量的HTTP工作程序（处理HTTP和RPC请求的子进程）。  
    一个选项允许限制和回收workers:
    ```editorconfig
       --limit-request <limit>
    ```   
    在回收和重新启动之前，工作人员将处理的请求数。默认为8196。
* 每个workers允许的最大虚拟内存 如果超出限制，则 workers 在当前请求结束时被终止并回收。默认为640MB。
    ```editorconfig
       --limit-memory-soft <limit>
    ```  
* 虚拟内存的硬限制，超过限制的任何 workers 将立即被杀死而无需等待当前请求处理的结束。默认为768MB。    
    ```editorconfig
       --limit-memory-hard <limit>
    ```  
* 防止工作程序为每个请求使用超过CPU秒数。如果超过限制，workers 将被杀死。默认为60。
    ```editorconfig
       --limit-time-cpu <limit>
    ```  
* 防止工作者花费超过几秒钟来处理请求。如果超过限制，workers 将被杀死。默认为120。  
不同于--limit-time-cpu 在于这是一个“挂起时间”限制，包括例如SQL查询。
    ```editorconfig
       --limit-time-real <limit>
    ```  
* 致力于cron工作的工人数量。默认为2.工作程序是多线程模式下的线程，是多处理模式下的进程。  
对于多处理模式，这是HTTP工作进程的补充。
    ```editorconfig
       --max-cron-threads <count>
    ```  
   
#### 实例
    
标题               | 描述 
------------------ | ---------------------------------------------------------
CPUs               | CPU核心数不是线程数
Physical           | 物理内存，不是虚拟内存或交换分区
workers            | 配置文件中指定的worker数（workers = x）
cron               | Number of workers for cron jobs (max_cron_threads = xx)
Mem Per            | 以MB为单位的内存，是每个workers请求的最大内存
Max Mem            | 所有workers可以使用的最大数量
limit_memory_soft  | 将用于此设置的字节数

注意：如果通知小于总内存，则最大内存是故意的。当workers处理请求时，他们可以超出Mem Per限制，因此负载较重的服务器可能会超过此数量。这就是内置“头部空间”的原因。

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
 
 注意：1MB = 1024kB, 1kB = 1024B. So 768 x 1024 x 1024 = 805306368 B
 
###  2. 依据上述资料进行计算，4核CPU，16G内存的odoo.conf配置如下

```editorconfig
    ;limit_memory_hard = (workers数量+ cron数量)  * 768M * 1024 * 1024(换算成字节)
    limit_memory_hard = 9663676416
        
    ;limit-memory-soft = (workers数量+ cron数量) * 640M * 1024 * 1024(换算成字节)
    limit-memory-soft = 8053063680
    
    limit_request  =  8192 
    limit_time_cpu  =  600 
    limit_time_real  =  1200
    max_cron_threads = 3
    
    ; workers = (CPU数量*2) + 1 ，多处理模式仅在基于 unix 的系统上可用
    workers = 9
    
``` 

## 优化数据库
1. 说明  
    * db_maxconn  指定每个odoo进程的 posgresql的最大物理连接数，但是对于所有数据库。默认64
        ```editorconfig
           --db_maxconn <limit>
        ```  
    * max_connections，默认100
        ```editorconfig
           --max_connections <limit>
        ```    
    * 以上参数必须满足以下条件，否则将会在运行时报错
        ```editorconfig
           (1 + workers + max_cron_threads) * db_maxconn < max_connections
        ```    
        

2. 配置odoo.conf  
    ```editorconfig
    
    ``` 
3. <a href="https://pgtune.leopard.in.ua" target="_blank">postgresql工具</a>

## Nginx加速
1. <a href="https://www.odoo.com/documentation/12.0/setup/deploy.html#https" target="_blank">参考官方文档</a>  
    有效提高网页加载速度。
2. 免费证书 
    *   部署在国内云服务器上的，可以使用云服务器厂商的证书。
    *   部署在局域网内部的服务器，可以使用<a href="https://letsencrypt.org/" target="_blank">Let's Encrypt</a>  
        80端口被封的情况，可以<a href="http://www.ituring.com.cn/article/211255" target="_blank">参考</a>  