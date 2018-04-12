# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 18:42:42 2018

@author: CS
"""

import os
import pandas as pd
import mysql.connector


conn = mysql.connector.connect(host="localhost",port=3306,user="root",\
                       password="输入自己的密码",database="symbols",charset="utf8")
cur = conn.cursor()
sql = 'USE symbols;'
cur.execute(sql)
filepath = 'E:\\symbols\\'
csvList = os.listdir(filepath)

for code in csvList:
    data = pd.read_csv(filepath+code,encoding="gbk")
    #数据库手动建表可以以纯数字作为表名，以代码建表不能以纯数字作为表名，报ProgrammingError
    sql2 = "CREATE TABLE stock_%s" % code[0:6] + "(\
    日期 DATE,\
    开盘价 DECIMAL(18,2),\
    最高价 DECIMAL(18,2),\
    最低价 DECIMAL(18,2),\
    收盘价 DECIMAL(18,2),\
    涨跌额 DECIMAL(18,2),\
    涨跌幅 FLOAT,\
    成交量 BIGINT,\
    成交额 BIGINT,\
    振幅 FLOAT,\
    换手率 FLOAT\
    )"
    cur.execute(sql2)
    print("%s" % code[0:6] + "is now storing.")
    length = len(data)
    for s in range(0,len(data)):
        record = tuple(data.loc[s])
        try:
            sql3 = "INSERT INTO stock_%s" % code[0:6] + "\
            (日期,开盘价,最高价,最低价,收盘价,涨跌额,涨跌幅,成交量,成交额,振幅,换手率)\
            VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " % record
            sql3 = sql3.replace('nan','null').replace('NaN','null')\
            .replace('None','null').replace('none','null')
            cur.execute(sql3)
        except:
            break


conn.commit()
cur.close()
conn.close()
        




























