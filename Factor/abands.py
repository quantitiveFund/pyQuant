# -*- coding: utf-8 -*-
'''
Acceleration Bands (ABANDS)
Description

The Acceleration Bands (ABANDS) created by Price Headley plots upper and lower envelope 
bands around a simple moving average. The width of the bands is based on the formula below.

Upper Band = Simple Moving Average (High * ( 1 + 4 * (High - Low) / (High + Low)))

Middle Band = Simple Moving Average

Lower Band = Simple Moving Average (Low * (1 - 4 * (High - Low)/ (High + Low)))
'''

import mysql.connector
import pandas as pd
import time
#import matplotlib.pyplot as plt

def loadfromMysql(code, start_date, end_date=time.strftime('%Y-%m-%d',time.localtime(time.time())), paralist = ['Date','Close']):
    #连接MySQL数据库
    conn = mysql.connector.connect(host="localhost",port=3306,user="root",\
                       password="*****",database="test",charset="utf8")
    cur = conn.cursor()
    ## 注意： where 从句里面输入的因子数值必须要加上单引号 where Date > '%s'"， 否则该where从句没有作用！！
    sql = "select %s from stock_%s where Date > '%s' and Date < '%s'" % \
    (','.join(paralist), code, start_date, end_date)
    try:
        cur.execute(sql)
        res = cur.fetchall()
        dat = pd.DataFrame(res, columns = paralist)
        dat = dat.set_index('Date')
        conn.close()
        return dat
    except:
        print('Error: unable to fetch data')

def abands(dat, lag = 10):
    mb = dat[['Close']].rolling(window = lag).mean()
    hi = dat[['High']]
    hi.columns=['p']
    lo = dat[['Low']]
    lo.columns=['p']
    ub = hi.mul(1 + 4 * (hi.sub(lo)).div(hi.add(lo)))
    lb = lo.mul(1 - 4 * (hi.sub(lo)).div(hi.add(lo)))

    ub = ub.rolling(window = lag).mean()
    lb = lb.rolling(window = lag).mean() 
    return mb, ub, lb
    

dat = loadfromMysql('603618', '2015-01-01', paralist = ['Date','Close','High','Low'])
mb, ub, lb = abands(dat, 10)


#plt.plot(mb)
#plt.plot(ub)
#plt.plot(lb)