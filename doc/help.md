## 用户类型
*  内部用户 - 是付费账号，占用系统资源/res_group_id=1
*  门户 - 是免费用户，不占用系统资源/res_group_id=9
*  公共 - /res_group_id=10


用户表单现在具有用户类型部分，仅在启用开发人员模式时可见。 它允许我们选择相互排斥的选项 - 内部用户，门户网站（外部用户，如客户）和publis（网站匿名访问者）。这已被更改，以避免内部用户也包含在门户网站或公共组中的错误配置 ，有效降低了他们的访问权限


Heading            | Description 
------------------ | ---------------------------------------------------------
CPUs               | Number of CPU Cores not threads
Physical           | Physical memory, not virtual or swap
workers            | Number of workers specified in config file (workers = x)
cron               | Number of workers for cron jobs (max_cron_threads = xx)
Mem Per            | Memory in MB that is the max memory for request per worker
Max Mem            | Maximum amount that can be used by all workers 
limit_memory_soft  | Number in bytes that you will use for this setting


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
 
 
(1 + workers + max_cron_threads) * db_maxconn < max_connections

workers = 1 (minimal value to make longpolling work)

max_cron_threads = 2 (default)

db_maxconn = 64 (default)

max_connections = 100 (default)