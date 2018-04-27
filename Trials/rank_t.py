# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 23:39:54 2018

@author: Administrator
"""

import mysql.connector

conn = mysql.connector.connect(host="10.23.0.2",port=3306,user="root",\
                       password="11031103",database="quant",charset="utf8")
cur = conn.cursor()


cur.execute('show tables')  # 罗列所有当前库里面的所有表格
tables = cur.fetchall()

open_price = []
date_str = '2018-04-13'
for tab in tables:
    sql = 'select open from ' +tab[0]+ ' where Date =' date_str
    