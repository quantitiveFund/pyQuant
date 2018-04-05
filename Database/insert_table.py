# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 21:06:27 2018

@author: Ni He
"""

import mysql.connector
import pandas as pd

conn = mysql.connector.connect(user='root', password='11031103', database='stockdata')
cursor = conn.cursor()
cursor.execute('create table stockname3 (id int unsigned auto_increment primary key, code varchar(20), name varchar(20), industry varchar(20), area varchar(20), IPO varchar(20))')
conn.commit()

f = pd.read_csv('datastockbasics.csv', header=0, usecols=[0,1,2,3,15], encoding='gbk')
sql = 'insert into stockname3 (code, name, industry, area, IPO) values (%s, %s, %s, %s, %s)'

for i in range(1,len(f)+1):
    cursor.execute(sql,["%06d"%(f[i-1:i]['code'][i-1]),f[i-1:i]['name'][i-1],f[i-1:i]['industry'][i-1],f[i-1:i]['area'][i-1],str(f[i-1:i]['timeToMarket'][i-1])])
    conn.commit()

cursor.close()
