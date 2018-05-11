# 获取面板数据

### 连接数据库

- **自主选择与数据库建立连接并返回codelist,conn,cur**

```connect
def connect():#连接数据库并返回股票池,conn,cur#
    while True:    
        ht = input('Please enter the host: ')
        pw = input('Please enter the password: ')
        db = input('Please enter the database: ')
        try:
            conn = mysql.connector.connect(host=ht, port=3306, user='root', 
            password=pw, database=db)  
            cur = conn.cursor()
            break
        except:
            re_try = input('Something might be wrong, or the datebase is not 
            available, do you want to retry (y/n)? ')
            if re_try == 'n' or re_try == 'no':
                break
    cur.execute('show tables')#展示数据库表格#
    codelist = cur.fetchall()#获取所有表格名#
    return codelist,conn,cur
```

- **使用实例**

```example
 codelist,conn,cur=connect()#无参数#
 
 Please enter the host: ****
 Please enter the password: ****
 Please enter the database: ****
 Successful connection
```

- **返回值**

1. **codelist**  股票池
2. **conn**  数据库地址
3. **cur**  光标地址，跨文件调用***loadfromMysql()***需传入此参数

___

### 获取历史数据

- **获取目标股票某段时间内的数据**

*初步测试读取速度优于pd.read_sql()*

```loadfromMysql
def loadfromMysql(code, cur, start_date='1990-12-19', end_date=time.strftime(
'%Y-%m-%d',time.localtime(time.time())), paralist=['Date','Close']):
## 注意： where 从句里面输入的因子数值必须要加上单引号 where Date >= '%s'"，否则该where从句没有用！！
    sql = "select %s from %s where Date >= '%s' and Date <= '%s'" % 
    (','.join(paralist), code, start_date, end_date)
    try:
        cur.execute(sql)#选择目标股票目标列目标区间#
        res = cur.fetchall()#抓取目标数据#
        data = pd.DataFrame(res, columns = paralist)
        data = dat.set_index('Date')
        return data
    except:
        print('Error: unable to fetch data. You might enter a wrong code')
```

- **参数说明**

1. *code*  **股票代码**‘stock_000001’
2. *cur*  **光标地址**connect()返回值
3. *start_date*  **开始日期**，默认'1990-12-19'(暂时无法获取准确IPO日期)
4. *end_date*   **结束日期**，默认'当天'
5. *paralist*     **数据列**，默认**['Date','Close']** #一列'Date'，另一列根据按需确定#

- **使用实例**

```example
data=loadfromMysql('stock_000001',cur,start_date='2014-04-11',end_date='2015-04-22')

            Close
Date             
2014-04-11  11.40
2014-04-14  11.28
2014-04-15  10.97
          ...
2015-04-20  16.30
2015-04-21  16.56
2015-04-22  16.95

[251 rows x 1 columns]
```

- **返回值**

**data**  股票历史数据

___

### 拼接面板数据

- **将指定日期及其滞后区间内多只股票的单个指标数据拼接成一张新的表**

####思路一

**(速度为思路二的3倍，500只股票7.6秒，可能是直接拼数据的原因)**

1. 指定日期，利用**loadfromMysql()**分别获取个股该日期前所有数据
2. 所得数据**从后往前取滞后天数**即为目标区间数据
3. 将所得数据拼接

#####获取滞后数据

```data_lag
def data_lag(data,lag):
    data_list=data.iloc[-(lag+1):]#滞后至当日  iloc[行数] loc[行名]#
    return data_list
```

- **参数说明**

1. *data*  **指定日期前的所有数据** 
2. *lag*  **滞后天数**

- **使用实例**

```example
data=loadfromMysql('stock_000001',cur,start_date='2014-04-11',end_date='2015-04-22')
data_lag(data,5)#当天+滞后5日=6天#

Date             
2015-04-15  16.65
2015-04-16  17.00
2015-04-17  16.93
2015-04-20  16.30
2015-04-21  16.56
2015-04-22  16.95
```

- **返回值**

**data_list**  滞后区间数据

___

##### 获取面板数据

```get_panel_data
def get_panel_data(codelist,cur,date,lag,target_columns=['Date','Close']):
    data0 = loadfromMysql('stock_000006',cur,end_date=date)#stock_000001不包括'2014-07-15'#
    data0_lag = data_lag(data0,lag)#获取标准索引#
    for code in codelist:
        data = loadfromMysql(code[0],cur,end_date=date,paralist=target_columns)#目标日期前数据#
        data_list = data_lag(data,lag)#目标区间数据#
        data_list.columns = [code[0]]#将列名改为股票名#
        data0_lag = pd.concat([data0_lag,data_list],axis=1,join_axes=[data0_lag.index])
        #根据标准索引拼接,无该日数据将赋值NA#
    data0_lag = data0_lag.drop(data0_lag.columns[0],axis=1)#删除首列#
    return data0_lag.dropna(axis=1)#删除区间内存在NA的列#
```

- **参数说明**

1. *codelist*  **目标股票池**
2. *cur*  **光标地址**，connect()返回值
3. *date*  **目标日期 **，同时为**end_date**
4. *lag*  **滞后天数**
5. *target_columns*  **股票目标指标**，默认值['Date','Close']

data0  获取标准索引(**权威指数**)

- **个人问题记录**

按stock_000001索引合并，**数据条数固定**，缺少'2014-07-15'，起始日往前拉伸，

其他完整股票‘2014-07-15’被忽视，而缺少延伸日数据，导致起始日为NA

- **使用实例**

```example
t1 = pd.datetime.now()
Open = get_panel_data(codelist[3:503],cur,'2015-04-22',250,target_columns=['Date','Open'])
t2 = pd.datetime.now()
print(t1-t2)

0:00:07.620696
```

![面板数据](C:\Users\edong\.spyder-py3\MyMarkdown\1526055251(1).jpg)

- **返回值**

**data0_lag.dropna(axis=1)**  目标区间内去除NA列的面板数据

___

####思路二

**（速度慢，500只股票22秒，可能是得到日期再分别读取区间的原因）**

1. 指定日期，利用**date_lage()**获取滞后区间的起始日期
2. 代入start_date和end_date，利用**loadfromMysql()**获取目标区间数据
3. 将所得数据拼接

##### 获取起始日期

```date_lag
def date_lag(date,lag):
    data = loadfromMysql('stock_000006',cur,end_date=date)#应使用上证指数为参考交易日#
    date_list = data.iloc[-(lag+1):].index#滞后至当日 iloc[行数] loc[行名]#
    date_start = date_list[0]#起始日#
    return date_start
```

- **参数说明**

1. *date*  **目标日期**
2. *lag*  **滞后天数**

- **使用实例**

```example
date_lag('2015-04-22',5)

'2015-04-15'
```

- **返回值**

**date_start**  滞后区间起始日

___

##### 获取面板数据

```get_panel_data
def get_panel_data(codelist,cur,date,lag,target_columns=['Date','Close']):
    temp=pd.Series()#临时列便于拼接#
    for code in codelist:
        date_start = date_lag(date,lag)#区间起始日期#
        data = loadfromMysql(code[0],cur,start_date=date_start,end_date=date,
        paralist=target_columns)
        data.columns = [code[0]]#列名改为股票名#
        temp = pd.concat([temp,data],axis=1)
        #不断拼接,先前temp所缺失的日期生成NA,覆盖到所有交易日('2014-07-15')#
    #del temp[0]删除初始列#
    return temp.dropna(axis=1)#删除区间包含NA列，包括第一列#
```

- **参数说明**

1. *codelist*  **目标股票池**
2. *cur*  **光标地址**，*connect()*返回值
3. *date*  **目标日期 **，同时为**end_date**
4. *lag*  **滞后天数**
5. *target_columns*  **股票目标指标**，默认值['Date','Close']

temp  临时序列用于**存储**拼接数据（**与data0不同，本身无标准索引**）

- **个人问题记录**

先前以stock_000001为标准交易日期，获取滞后区间起始日期，得到'2014-04-11'至'2015-04-22'，

后来发现缺少正常交易日'2014-07-15'

```difference
Close.index[~Close.index.isin(Open.index)]
```

但经过不断拼接，其他股票填补该日空缺，导致数据**多出一行**

- **使用实例**

```example
t3=pd.datetime.now()
Close=get_panel_data(codelist[3:503],cur,'2015-04-22',250)
t4=pd.datetime.now()
print(t3-t4)

0:00:22.274597
```

- **返回值**

**temp.dropna(axis=1)**  目标区间内去除NA列的面板数据





