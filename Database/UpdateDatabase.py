# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 01:13:18 2018

@author: Pikari
"""

import mysql.connector
import pandas as pd
import datetime as dt
from WindPy import w
w.start()

def create_table(table_name, columns, data_type):
    try:
        temp = ''
        for i in range(len(columns)):
           temp += columns[i] + ' ' + data_type[i] + ', '   
        temp = 'create table ' + table_name + '(' + temp[:-2] + ')'
        cursor.execute(temp)
        print('\033[0;32m' + table_name + ' creating compete' + '\033[0m')
    except:
        print('\033[0;31m' + table_name + ' had already existed' + '\033[0m')

def insert_table(table_name, columns, data):
    try:
        sql = 'insert into ' + table_name + ' ('  + '%s, ' * len(columns) + ')'
        sql = sql[:-3] + sql[-1]
        sql = sql%tuple(columns) + ' values ' + '(' +'%s, ' * len(columns) + ')'
        sql = sql[:-3] + sql[-1]
        for i in range(1, len(data)+1):
            temp = [str(data.index[i-1]), data.OPEN[i-1], data.HIGH[i-1], data.LOW[i-1], data.CLOSE[i-1], data.CHG[i-1], round(data.PCT_CHG[i-1], 2), int(round(data.VOLUME[i-1]/100, 0)), int(round(data.AMT[i-1]/10000, 0)), round(data.SWING[i-1], 2), round(data.TURN[i-1], 2)]
            cursor.execute(sql, temp)
        conn.commit()
        print('\033[0;32m' + table_name + ' updating compete' + '\033[0m')
    except:
        print('\033[0;31m' + table_name + ' no need to be updated' + '\033[0m')

def get_date(table_name):
    try:
        cursor.execute('select Date from ' + table_name + ' order by Date desc limit 1')
        date = cursor.fetchall()[0][0]
        return date
    except:
        print('\033[0;31m' + table_name + ' has no latest date' + '\033[0m')

def update(table_name, columns):
    latest_date = get_date(table_name)
    if latest_date == None:
        data = w.wsd(code, d, 'ipo')
    else:
        data = w.wsd(code, d, str(dt.datetime.strptime(latest_date, '%Y-%m-%d') + dt.timedelta(days=1)), str(dt.datetime.now()))
    data = pd.DataFrame(data.Data, index=data.Fields, columns=data.Times).T
    insert_table(table_name, columns, data)
       
conn = mysql.connector.connect(host='10.23.0.2', port=3306, user='root', password='******', database='quant')  
cursor = conn.cursor()

code_list = w.wset("SectorConstituent","sectorId=a001010100000000;field=wind_code").Data[0]
#code_list = ['603617.sh', '603618.sh', '603619.sh', '603648.sh', '603659.sh', '000830.sz']
global d
d = ["open, high, low, close, chg, pct_chg, volume, amt, swing, turn"]
    
columns = ['Date', 'Open', 'High', 'Low', 'Close', 'ChgAmount', 'ChgRate', 'Volume', 'VolTrans', 'Swing', 'Turnover']
data_type = ['text null', 'float null', 'float null', 'float null', 'float null', 'float null', 'float null', 'float null', 'float null', 'float null', 'float null']

cursor.execute('show tables')
tables = cursor.fetchall()

for code in code_list:
    table_name = 'stock_' + code[:6]
    if (table_name,) in tables:
        update(table_name, columns)
    else:
        create_table(table_name, columns, data_type)
        update(table_name, columns)
