# 如何使用在Python的time和datetime模块



https://blog.csdn.net/mouday/article/details/80231010

![img](https://img-blog.csdn.net/20180507201831731?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L21vdWRheQ==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70) 

说明： 

绿色线条：timestamp -> datetime对象路径 

橙色线条：datetime对象 -> timestamp路径 

灰色线条：time模块 与 datetime模块 分界过渡

时间的四个存在方式

- 时间戳，float
- 元组形式， struct_time
- 字符串形式，str
- 时间对象  datetime， time

代码实例

导入模块

```
# -- coding:utf-8 --

import time

from datetime import datetime

from datetime import date

from datetime import timedelta

```

一、时间的获取

```Python
1、获取当前时间的时间戳

t = time.time()

<type 'float'>, 1525687472.870682

2、获取当前时间元组

t = time.localtime()

 <type 'time.struct_time'>,

time.struct_time(tm_year=2018, tm_mon=5, tm_mday=7, tm_hour=18, 

tm_min=5, tm_sec=47, tm_wday=0, tm_yday=127, tm_isdst=0))

3、获取当前时间的字符串

本地时间

t1 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

t2 = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

# utc时间：就是0时区的区时,比北京时间晚8小时

t3 = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

t4 = time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())

<type 'str'>, '2018-05-07 18:03:38'

<type 'str'>, '2018-05-07 18:03:38'

<type 'str'>, '2018-05-07 10:03:38'

<type 'str'>, '2018-05-07 10:03:38'

4、获取时间对象

# 获取当前日期和时间 datetime

t = datetime.now()

# (<type 'datetime.datetime'>, 

# datetime.datetime(2018, 5, 7, 18, 10, 13, 538265))

# 获取当前日期 date

t1 = datetime.now().date()

# (<type 'datetime.date'>, datetime.date(2018, 5, 7))

# 获取当前时间 time

t2 = datetime.now().time()

# (<type 'datetime.time'>, datetime.time(18, 11, 4, 939271))

```



二、时间的计算

```python
t = datetime.now() - timedelta(days=3)
```



三、时间形式之间的转换

``` python
1、时间戳与时间元组

# 时间戳 -> 时间元组:

t = time.localtime(1525681106.08)

# 时间元组 -> 时间戳

t = time.mktime(time.localtime())

2、时间元组与字符串

# 时间元组 -> 字符串

t = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

# 字符串 ->  时间元组

t = time.strptime("2018-01-07 17:26:24","%Y-%m-%d %H:%M:%S")

3、时间戳与字符串

# 时间戳 -> 字符串

t = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(1525681106.08))

t = datetime.fromtimestamp(1525681106.08).strftime("%Y-%m-%d %H:%M:%S")

# 字符串 -> 时间戳：

t = time.mktime(time.strptime("2018-01-07 17:26:24","%Y-%m-%d %H:%M:%S"))

4、时间戳与datetime对象

# 时间戳 -> datetime对象

t = datetime.fromtimestamp(1525681106.08)

# UTC

t = datetime.utcfromtimestamp(1525681106.08)  

# datetime对象 -> 时间戳

t = time.mktime(datetime.now().timetuple())

# 不过要注意的是time是从1900开始计算的。而datetime包含1-9999的范围

5、时间元组与datetime对象

# 时间元组对象 -> datetime对象 

t = datetime.fromtimestamp(time.mktime(time.localtime()))

# datetime对象 -> 时间元组对象

t = datetime.now().timetuple()

6、字符串与datetime对象

# str字符串 -> datetime对象 

t = datetime.strptime("2018-01-07 17:26:24", "%Y-%m-%d %H:%M:%S")

# datetime对象 -> str字符串

t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

7、datetime, data, time 对象之间转换

# datetime对象 -> date对象

t1 = datetime.now().date() 

# datetime对象 -> time对象

t2 = datetime.now().time()

# date对象 + time对象 -> datetime对象

t = datetime.combine(t1, t2)

# <type 'datetime.datetime'>

8、date对象与时间戳

# 时间戳  ->  date对象

t = date.fromtimestamp(time.time())
```







参考：

1. Python编程：time时间模块
2. https://blog.csdn.net/mouday/article/details/78996561
3. time，datetime中字符串，时间对象，和时间戳的转换学习整理
4. https://blog.csdn.net/hzx3739/article/details/50117967