# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 21:06:27 2018

@author: Ni He
"""
import mysql.connector
import pandas as pd

conn = mysql.connector.connect(host='10.23.0.2', port=3306, user='root', password='*****', database='quant')
cursor = conn.cursor()


# 新建总表
cursor.execute('create table stockname (id int unsigned auto_increment primary key, code varchar(20), name varchar(20), industry varchar(20), area varchar(20), IPO varchar(20))')
conn.commit()

f = pd.read_csv('datastockbasics.csv', header=0, usecols=[0,1,2,3,15], encoding='gbk')
sql = 'insert into stockname (code, name, industry, area, IPO) values (%s, %s, %s, %s, %s)'

#for i in range(1,len(f)+1):
#    cursor.execute(sql,["%06d"%(f[i-1:i]['code'][i-1]),f[i-1:i]['name'][i-1],f[i-1:i]['industry'][i-1],f[i-1:i]['area'][i-1],str(f[i-1:i]['timeToMarket'][i-1])])
#    conn.commit()

for i in range(1,len(f)+1):
    if f[i-1:i]['timeToMarket'][i-1] == 0:
        ipo = ''
    else:
        ipo = str(f[i-1:i]['timeToMarket'][i-1])
    cursor.execute(sql, ["%06d"%(f[i-1:i]['code'][i-1]),f[i-1:i]['name'][i-1],f[i-1:i]['industry'][i-1],f[i-1:i]['area'][i-1],ipo])
    conn.commit()

# 新建数据表  以下部分还未测试

sql = 'SELECT code FROM stockname'
try:
   cursor.execute(sql)
   # 获取所有记录列表
   results = cursor.fetchall()
   for rows in results:
       filename = rows[0] + '.csv'
       try:
          f = pd.read_csv(filename, header=0, encoding='gbk') 
          cursor.execute('create table '+'s'+rows[0]+ ' (id int unsigned auto_increment primary key, date varchar(20), \
          open float(20), close float(20), high float(20), low float(20), vol float(20))')
          conn.commit()
          sql = 'insert into '+'s'+rows[0]+ '(date, open, close, high, low, vol) values (%s, %f, %f, %f, %f, %f)'
          for i in range(1,len(f)+1):
              cursor.execute(sql,f[i-1:i]['date'][i-1],float('%.3f' % f[i-1:i]['open'][i-1]),float('%.3f' % f[i-1:i]['close'][i-1]), \
              float('%.3f' % f[i-1:i]['high'][i-1]),float('%.3f' % f[i-1:i]['low'][i-1]),float('%.3f' % f[i-1:i]['volume'][i-1]))
              conn.commit()
       except:
            print('没有数据文件'+filename)  
except:
   print ("Error: unable to fetch data")
cursor.close()
