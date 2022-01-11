# 说明

windows主机更新安装Visual C++ [链接](https://docs.microsoft.com/zh-CN/cpp/windows/latest-supported-vc-redist?view=msvc-170) 

linux主机需要编译gcc,建议直接编译最新的。 [参考链接](https://ywnz.com/linuxjc/7264.html)
```
sudo cp /usr/bin/gcc /usr/bin/gcc8.3.0
sudo rm /usr/bin/gcc /usr/bin/gcc
sudo ln -s /usr/local/gcc/bin/gcc   /usr/bin/gcc
sudo ln -s /usr/local/gcc/bin/gcc   /home/rain/anaconda3/envs/odoo14/bin/gcc
```


# Linux root conda环境 设置
```
临时增加conda 环境变量
export PATH=/home/monk/anaconda3/bin:$PATH

# 创建conda虚拟环境, odoo14 是环境名称
conda create --name odoo14 python=3.8.12

查看已有的虚拟环境
conda env list

# 激活环境
source activate

# 退出环境
source deactivate

# 切换到想要的虚拟环境
conda activate odoo14

# 删除环境
conda remove -n odoo14 --all

#安装requirements.txt中的python包
pip install -r requirements.txt -i https://pypi.doubanio.com/simple 
```

# Linux root conda环境 升级gxx
```
# 将 conda-forge 包安装到现有的 conda 环境中
conda config --add channels conda-forge
conda config --set channel_priority strict

# 要使用conda安装此软件包，请运行以下操作之一：
conda install -c conda-forge gcc
conda install -c conda-forge/label/broken gcc
conda install -c conda-forge/label/cf201901 gcc
conda install -c conda-forge/label/cf202003 gcc

```
```
conda search gxx
conda install -c conda-forge gxx

ln -s /home/rain/anaconda3/envs/odoo14/libexec/gcc/x86_64-conda-linux-gnu/11.2.0/gcc    /home/rain/anaconda3/envs/odoo14/bin/gcc
ln -s /home/rain/anaconda3/envs/odoo14/libexec/gcc/x86_64-conda-linux-gnu/11.2.0/gcc /home/rain/anaconda3/envs/odoo14/bin/c++
ln -s /home/rain/anaconda3/envs/odoo14/libexec/gcc/x86_64-conda-linux-gnu/11.2.0/gcc /home/rain/anaconda3/envs/odoo14/bin/cpp

conda deactivate
conda activate odoo14

```

```
先编译升级gcc11.2.0
在创建conda环境
which gcc && gcc --version
conda install -c conda-forge gcc_linux-64=11.2.0=h39a9532_3
cd /home/rain/anaconda3/envs/odoo14/bin
ln -s /home/rain/anaconda3/envs/odoo14/bin/x86_64-conda_cos6-linux-gnu-cc gcc
ln -s /home/rain/anaconda3/envs/odoo14/bin/x86_64-conda_cos6-linux-gnu-cpp g++

```

