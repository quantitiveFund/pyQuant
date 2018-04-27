# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 01:13:18 2018

@author: Pikari
"""

import mysql.connector
import pandas as pd
import datetime as dt
from WindPy import w
import time
import os
w.start()

def create_table(table_name, columns, data_type):
    try:
        temp = ''
        for i in range(len(columns)):
           temp += columns[i] + ' ' + data_type[i] + ', '   
        temp = 'create table ' + table_name + '(' + temp[:-2] + ')'
        cursor.execute(temp)
        print('\033[0;32m' + table_name + ' has been nearly created.' + '\033[0m')
    except:
        # 这儿为什么会无法创建表格？除非前头出现语法错误？ 这个问题事实上不会出现的
        print('\033[0;31m' + table_name + ' had already existed' + '\033[0m')
        flog.writelines('The table ' + table_name + ' can not be created !? \n')

def insert_table(table_name, columns, data):
    try:
        sql = 'insert into ' + table_name + ' ('  + '%s, ' * len(columns) + ')'
        sql = sql[:-3] + sql[-1]
        sql = sql%tuple(columns) + ' values ' + '(' +'%s, ' * len(columns) + ')'
        sql = sql[:-3] + sql[-1]
        # 这儿强制将Nan的数据转成0， 即停牌的情况，收盘价沿用停牌前一天，其他数据都为零， Wind的规则是其他数据都是NAN
        data = data.where(data.notnull(), 0)
        for i in range(1, len(data)+1):
            temp = [str(data.index[i-1]), round(float(data.OPEN[i-1]),2), round(float(data.HIGH[i-1]),2), round(float(data.LOW[i-1]),2), \
                    round(float(data.CLOSE[i-1]),2), round(float(data.CHG[i-1]),2), round(float(data.PCT_CHG[i-1]), 2), \
                    int(round(data.VOLUME[i-1]/100, 0)), int(round(data.AMT[i-1]/10000, 0)), \
                    round(float(data.SWING[i-1]), 2), round(float(data.TURN[i-1]), 2)]
            cursor.execute(sql, temp)
        conn.commit()
        print('\033[0;32m' + table_name + ' content has been updated competely' + '\033[0m')
    except:
        # WIND 在交易数据来到之前，会出现这个问题
        print('\033[0;31m Error in updating ' + table_name + '. Please update after a trading day.' + '\033[0m')
        flog.writelines('The content of table ' + table_name + ' can not be updated !\n')

def get_date(table_name):
    try:
        cursor.execute('select Date from ' + table_name + ' order by Date desc limit 1')
        date = cursor.fetchall()[0][0]
        return date
    except:
        # 这个例外出现是什么原因？除非这个表格是存在的，但是没有任何数据，如果是这样，是不是在这儿应该ruturn None
        print('\033[0;31m' + table_name + ' has no latest date' + '\033[0m')
        flog.writelines('Cannot get the latest date on ' + table_name + '\n')
        return None

def update(table_name, columns):
    latest_date = get_date(table_name)
    if latest_date == None:
        data = w.wsd(code, d, 'ipo')
    elif latest_date == time.strftime('%Y-%m-%d',time.localtime(time.time())):
        print('\033[0;32m' + table_name + ' is up to date. ' + '\033[0m')
        return
    else:
        data = w.wsd(code, d, str(dt.datetime.strptime(latest_date, '%Y-%m-%d') + dt.timedelta(days=1)), str(dt.datetime.now()))
    data = pd.DataFrame(data.Data, index=data.Fields, columns=data.Times).T
    insert_table(table_name, columns, data)
    

while True:
    hostname = input('Please enter the hostname: ')
    pw = input('Please enter the password: ')
    dbname = input('Please enter the number of datebase: ')
    try:
        conn = mysql.connector.connect(host=hostname, port=3306, user='root', password=pw, database=dbname)  
        cursor = conn.cursor()
        break
    except:
        re_try = input('The password might be wrong, or the datebase is not available, do you want to retry (y/n)? ')
        if re_try == 'n' or re_try == 'no':
            break
          

code_list = w.wset("SectorConstituent","sectorId=a001010100000000;field=wind_code").Data[0]
#code_list = ['603617.sh', '603618.sh', '603619.sh', '603648.sh', '603659.sh', '000830.sz']
global d
d = ["open, high, low, close, chg, pct_chg, volume, amt, swing, turn"]
    
columns = ['Date', 'Open', 'High', 'Low', 'Close', 'ChgAmount', 'ChgRate', 'Volume', 'VolTrans', 'Swing', 'Turnover']
data_type = ['text null', 'float null', 'float null', 'float null', 'float null', 'float null', 'float null', 'float null', 'float null', 'float null', 'float null']


cursor.execute('show tables')
tables = cursor.fetchall()
# Open the log file 
fname = os.getcwd() + '\\log.txt'
flog = open(fname, 'a+')
flog.writelines('\n \n Date Updating Log on ' + time.strftime('%Y-%m-%d',time.localtime(time.time())) + '\n')
flog.writelines('Start from: '+ time.strftime('%H:%M:%S',time.localtime(time.time())) + '\n')


for code in code_list:
    table_name = 'stock_' + code[:6]
    if (table_name,) in tables:
        update(table_name, columns)
    else:
        create_table(table_name, columns, data_type)
        update(table_name, columns)

flog.writelines('Update finished at: '+ time.strftime('%H:%M:%S',time.localtime(time.time())) + '\n')
flog.close()