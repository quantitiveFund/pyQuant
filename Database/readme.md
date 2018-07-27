# MariaDB #

MariaDB是MySQL的一个分支，其使用方法和MySQL基本一致。百度百科的基本介绍 [请点击](https://baike.baidu.com/item/mariaDB/6466119?fr=aladdin)

## MariaDB下载 ##
MariaDB可以在多种平台上使用，Windows平台的下载版本 MariaDB 10.2.14 稳定版，发布时间2018-03-27

下载地址为：[64位](https://downloads.mariadb.org/interstitial/mariadb-10.2.14/winx64-packages/mariadb-10.2.14-winx64.msi/from/http%3A//mirrors.tuna.tsinghua.edu.cn/mariadb/) | [32位](https://downloads.mariadb.org/interstitial/mariadb-10.2.14/win32-packages/mariadb-10.2.14-win32.msi/from/http%3A//mirrors.tuna.tsinghua.edu.cn/mariadb/) （32位可以在百度网盘[下载](https://pan.baidu.com/s/1Q-etGpyKBkdoDdu8eoZVBA) 密码：bpyc）

安装MariaDB时候需要设置，MariaDB会提示输入root用户的口令，**请务必记清楚** （否则貌似需要重新安装才可以调整口令，另外my.ini文件在所有程序 -> MariaDB 里面）。在Windows上，安装时请选择UTF-8编码，以便正确地处理中文。在安装过程中，其他端口的选择都选择默认3306，主机名称 localhost。

服务器 Windows Server 2003 适合版本 5.5.33a 32位 [下载地址](https://downloads.mariadb.org/interstitial/mariadb-5.5.33a/win32-packages/mariadb-5.5.33a-win32.msi/from/http%3A//ftp.hosteurope.de/mirror/archive.mariadb.org/?serve)

## MariaDB 驱动 ##

需要支持Python的MySQL驱动来连接到MySQL服务器。MySQL官方提供了mysql-connector-python驱动，但是安装的时候需要给pip命令加上参数--allow-external：

`$ pip install mysql-connector-python --allow-external mysql-connector-python`  （测试可用）

如果上面的命令安装失败，可以试试另一个驱动：

`$ pip install mysql-connector`  （这个没有经过测试）

## MariaDB 客户端查看 Navicat ##

使用Navicat MySQL版本可以方便查看MySQL 和 MariaDB数据库的内容。

百度网盘 [下载](https://pan.baidu.com/s/12BGID7lWlpKyeKfnCxKsmw)  密码：wqtp

将上述资料下载到硬盘里面即可直接使用，点击根目录底下的 navicat.exe 即可。

软件需要注册：名称和组织不用填写，注册码填写： NAVH-WK6A-DMVK-DKW3

设置连接，新建数据库，修改数据库都可以在Navicat里面完成。

## Python 连接数据库 ##

`import mysql.connector`

`conn = mysql.connector.connect(host='10.23.0.2', port=3306, user='root', password='******',database='quant',charset='utf8')` 该数据库是手动建立的，请填上相应的密码

`cursor = conn.cursor()` 以上三行是数据库连接命令

`cursor.execute('create table stockname (id varchar(20) primary key, name varchar(20), code varchar(20))')`  建表可以在Navicat中完成

`cursor.execute('insert into stockname (id, name, code) values (%s, %s, %s)', ['1', '中国石油', '600001'])`

`conn.commit()` 完成数据库建表以及插入工作

`cursor.close()` 关闭数据库

## 使用SQLAlchemy

SQLAlchemy使用了一个所谓ORM技术：Object-Relational Mapping，简单可以理解成把关系数据库的表结构映射到对象上。也就是使用Class的一个实例去存储一个表，然后可以很方便的使用SQLAlchemy的一些函数来进行数据库表格的操作，而不需要使用大量的SQL语句。

安装方法
`pip install sqlalchemy`
初始化的方法：
`from sqlalchemy import create_engine`
`engine = create_engine('mysql+mysqlconnector://root:password@localhost:3306/test')`
然后可以使用如：
`engine.execute('select * from ....')`
执行通常的SQL语句来操作数据库。
其他一个非常大的好处，就是可以将Pandas的DataFrame直接读出，或者写入MySQL。
注意使用方法
`pd.io.sql.to_sql(DataFrame, table_in_database, engine, schema = database, if_exists = 'append'or'replace'`
`target_DataFrame = pd.read_sql_query('select * from table',engine)`
