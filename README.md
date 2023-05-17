# 说明

## 一、 新环境部署

### 1. 准备配置文件
根据模板settings.ini.template，生成settings.ini文件放在项目根目录下。

### 2. 虚拟环境
#### 安装
- linux
```shell
cd PROJECT_PATH
python3 -m venv venv

source venv/bin/activate
pip install -r requirements.txt
```
安装mysqlclient的时候，如果系统版本为CentOS/Rocky Linux，MySQL版本在8.0以上，可能会出现
“OSError: mysql_config not found”的错误，可以用下面的办法修复：<br>
>yum provides mysql_config<br>yum install mariadb-connector-c-devel-3.2.6-1.el9_0.x86_64

- windows

```shell
cd PROJECT_PATH
python3 -m venv venv

.\venv\bin\activate.bat
pip install -r requirements.txt
```

#### 进入虚拟环境
```shell
source venv/bin/activate
```

### 3. 准备数据库
#### 创建数据库并迁移
```sql
CREATE DATABASE DATABASE_NAME DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```
```shell
python manage.py migrate
```
#### 或执行重建命令
```shell
python tools/init_mysql
```

### 4. 初始化用户、组，并初始化权限
```shell
python manage.py init_users
python manage.py update_perms
```

### 5. 静态文件上传
上传static下的文件到s3存储
```shell
python manage.py upload_static
```

### 6. 国际化（可选）
```shell
# 生成po文件
django-admin makemessages
# 编译成mo文件
django-admin compilemessages -l zh_Hans
```

## 二、数据库备份与还原

### 1. 手动备份
```shell
python manage.py backup_dbs
```
> --path参数指定备份路径。默认会备份到/home/db_backups/[数据库名]

### 2. 定时备份
```shell
crontab -e
# 加入定时任务（使用项目绝对路径）
1 2 * * * PROJECT_PATH/venv/bin/python PROJECT_PATH/manage.py backup_dbs
```
> 注意替换路径

### 3. 数据库还原
危险操作，会清空数据库，并从sql文件导入数据。
- 导入sql文件
```shell
python tools/restore_mysql.py SQL_FILE_PATH
```
> 注意替换路径。

### 4. 重置环境
危险操作，只用于开发环境重置环境用，会清理迁移文件，删除数据库并重建。
```shell
python tools/init_mysql.py
```