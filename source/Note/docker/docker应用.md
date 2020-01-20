#  Docker 应用



### docker 运行 mysql

- 获取镜像

  ```bash
  # 从docker hub的仓库中拉取mysql镜像
  sudo docker pull mysql
  ```

- 运行一个mysql实例

  ```bash
  docker run --name fp-mysql -p 23306:3306 -e MYSQL_ROOT_PASSWORD=123456 -d mysql:5.6
  
  5b6bf6f629bfe46b4c8786b555d8db1947680138b2de1f268f310a15ced7247a
  
  
  run            运行一个容器
  --name         后面是这个镜像的名称
  -p 3306:3306   表示在这个容器中使用3306端口(第二个)映射到本机的端口号也为3306(第一个)
  -d             表示使用守护进程运行，即服务挂在后台
  
  ```

- 装一个mysql-client，访问mysql数据库

  ```bash
  
  sudo apt-get install mysql-client-core-5.6
  
  # mysql命令访问服务器
  mysql -h 192.168.95.4 -P 3306 -uroot -p 123456
  ```

- 

