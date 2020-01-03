
### 远程连接

#### 连接远程服务器

```shell
ssh root@192.168.163.129
```



#### iterm 添加连接文件

- 可以在`～/.ssh/` 下面写一个脚本，	`~/.ssh/server-test`

  ```
  #!/usr/bin/expect -f
  set user root
  set host 192.168.1.110
  set password 123456
  set timeout -1
  
  spawn ssh $user@$host
  expect "*assword:*"
  send "$password\r"
  interact
  expect eof
  ```

- iTerm2 的`Profiles`  新建一个`profile`，`Command` 里填入 `expect ~/.ssh/server-test`

  

### 文件传输

#### 1、上传本地文件到服务器

```
scp /path/filename username@servername:/path/
```

例如`scp /var/www/test.php root@192.168.0.101:/var/www/` 把本机`/var/www/`目录下的test.php文件上传到`192.168.0.101`这台服务器上的`/var/www/`目录中



#### 2、从服务器上下载文件

下载文件我们经常使用wget，但是如果没有http服务，如何从服务器上下载文件呢？

```
scp username@servername:/path/filename /var/www/local_dir（本地目录）
```

例如`scp root@192.168.0.101:/var/www/test.txt` 把`192.168.0.101`上的`/var/www/test.txt` 的文件下载到`/var/www/local_dir`（本地目录）

 

#### 3、从服务器下载整个目录

```
scp -r username@servername:/var/www/remote_dir/（远程目录） /var/www/local_dir（本地目录）
```

例如:`scp -r root@192.168.0.101:/var/www/test /var/www/`

 

#### 4、上传目录到服务器

```
scp -r local_dir username@servername:remote_dir
```

例如：`scp -r test root@192.168.0.101:/var/www/` 把当前目录下的test目录上传到服务器的`/var/www/` 目录



### Bash 脚本连接

- 执行多条命令

  ```shell
  #!/bin/bash
  ssh user@remoteNode << eeooff
  cd /home
  touch abcdefg.txt
  exit
  eeooff
  echo done!
  ```

  

  ```shell
  #!/bin/bash  
    
  #变量定义  
  ip_array=("192.168.1.1" "192.168.1.2" "192.168.1.3")  
  user="test1"  
  remote_cmd="/home/test/1.sh"  
    
  #本地通过ssh执行远程服务器的脚本  
  for ip in ${ip_array[*]}  
  do  
      if [ $ip = "192.168.1.1" ]; then  
          port="7777"  
      else  
          port="22"  
      fi  
      ssh -t -p $port $user@$ip "remote_cmd"  
  done  
  ```

  

