
### 进程常用命令

```shell
# 后台不停止运行test脚本，并将脚本日志写到test.log 
nohup ./test.sh  > test.log &

# 搜索当前运行的进程
ps aux | grep start 

# 查看端口占用
lsof -i:端口号

# 杀死进程
kill -9 ppid

# 进程监控工具
top 
```
 

 ### 文件常用命令  
 ```shell
# 查看日志中最近出现的字符str
tail -f test.log | grep str

# 使用通配符*(0或者任意多个)。表示在/etc目录下查找文件名中含有字符串‘srm’的文件
find /etc -name '*srm*'　　

# 修改文件目录权限
chmod -R 755 /upload
  # -rwxr-xr-x (755) 只有所有者才有读，写，执行的权限，组群和其他人只有读和执行的权限
  
# 更改文件目录所属用户
chown - R $USER /tmp/

# 查看系统用户：
cat /etc/passwd
 ```



### 网络相关命令

```shell
# 查询、配置网络卡与 IP 网域等相关参数
ifconfig

# 域名解析命令,进行域名与IP地址解析
nslookup [主机名或者IP]     
> server

# 查看连接的网络服务
netstat -an | grep ESTABLISHED

# 查看路由表（网关）
netstat -rn 


cat /etc/hosts：      域名到 IP 地址的映射。
cat /etc/networks：   网络名称到 IP 地址的映射。
cat /etc/resolv.conf：DNS域名地址
cat /etc/protocols：  协议名称到协议编号的映射。
cat /etc/services：   TCP/UDP 服务名称到端口号的映射。
```





