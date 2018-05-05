# -*- coding: utf-8 -*-
"""
Created on Sat May  5 01:18:58 2018
https://zhuanlan.zhihu.com/p/29519040
@author: Ni He
"""

from pandas import DataFrame, Series
import pandas as pd; import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from matplotlib import ticker as mticker
from matplotlib.finance import candlestick_ohlc
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY,YEARLY
from matplotlib.dates import MonthLocator,MONTHLY
import datetime as dt
import pylab
import mysql.connector
import time

def loadfromMysql(code, start_date, end_date=time.strftime('%Y-%m-%d',time.localtime(time.time())), paralist = ['Date','Close']):
    #连接MySQL数据库
    while True: 
        hostname = 'localhost'
        pw = input('Please enter the password: ')
        try:
            conn = mysql.connector.connect(host = hostname, port=3306, user='root', password = pw, database='quant')  
            cur = conn.cursor()
            break
        except:
            re_try = input('The password might be wrong, or the datebase is not available, do you want to retry (y/n)? ')
            if re_try == 'n' or re_try == 'no':
                break

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
        print('Error: unable to fetch data. You might enter a wrong code')
        
        

days = loadfromMysql(code ='603618', start_date = '2015-01-01', paralist = ['Date','Open','Close','High','Low','Volume'])
days = days.sort_index()
days.index.name = 'DateTime'
daysreshape = days.reset_index()
# convert the datetime64 column in the dataf rame to 'float days'
for i in range(0,len(daysreshape['DateTime'])):
    daysreshape['DateTime'][i]=mdates.date2num(dt.datetime.strptime(daysreshape['DateTime'][i], '%Y-%m-%d'))

#daysreshape['DateTime']=mdates.date2num(daysreshape['DateTime'].astype(dt.datetime))
daysreshape = daysreshape.reindex(columns=['DateTime','Open','High','Low','Close','Volume']) 
#daysreshape[['Open','High','Close','Low','Volume']] = daysreshape[['Open','High','Close','Low','Volume']].apply(pd.to_numeric, errors='coerce')
daysreshape[['Open','High','Close','Low','Volume']] = daysreshape[['Open','High','Close','Low','Volume']].astype(float) 

MA1 = 10  
MA2 = 50
Av1  = daysreshape['Close'].rolling(window = MA1).mean().astype('float')  
Av2  = daysreshape['Close'].rolling(window = MA2).mean().astype('float')  
#Av1 = movingaverage(daysreshape.Close.values, MA1)
#Av2 = movingaverage(daysreshape.Close.values, MA2)
SP = len(daysreshape.DateTime.values[MA2-1:])
fig = plt.figure(facecolor='#07000d',figsize=(15,10))
    
ax1 = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4, axisbg='#07000d')
candlestick_ohlc(ax1, daysreshape.values[-SP:], width=.6, colorup='#ff1717', colordown='#53c156')
Label1 = str(MA1)+' SMA'
Label2 = str(MA2)+' SMA'
    
ax1.plot(daysreshape.DateTime.values[-SP:],Av1.values[-SP:],'#e1edf9',label=Label1, linewidth=1.5)
ax1.plot(daysreshape.DateTime.values[-SP:],Av2.values[-SP:],'#4ee6fd',label=Label2, linewidth=1.5)
ax1.grid(True, color='w')
ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax1.yaxis.label.set_color("w")
ax1.spines['bottom'].set_color("#5998ff")
ax1.spines['top'].set_color("#5998ff")
ax1.spines['left'].set_color("#5998ff")
ax1.spines['right'].set_color("#5998ff")
ax1.tick_params(axis='y', colors='w')
plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
ax1.tick_params(axis='x', colors='w')
plt.ylabel('Stock price and Volume')
plt.show()


# Volume info
volumeMin = 0
ax1v = ax1.twinx()
#ax1v.fill_between(daysreshape.DateTime.values[-SP:],volumeMin, days.Volume.values[-SP:].astype(int), facecolor='#00ffe8', alpha=.4)
ax1v.fill_between(daysreshape.DateTime.values[-SP:].astype(int),volumeMin, days.Volume.values[-SP:].astype(int), facecolor='#00ffe8', alpha=.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.grid(False)
    ###Edit this to 3, so it's a bit larger
ax1v.set_ylim(0, 4*days.Volume.values.astype(int).max())
ax1v.spines['bottom'].set_color("#5998ff")
ax1v.spines['top'].set_color("#5998ff")
ax1v.spines['left'].set_color("#5998ff")
ax1v.spines['right'].set_color("#5998ff")
ax1v.tick_params(axis='x', colors='w')
ax1v.tick_params(axis='y', colors='w')

