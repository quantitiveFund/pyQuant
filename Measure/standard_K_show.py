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
        pw = input('Please enter the password: ')
        try:
            conn = mysql.connector.connect(host='10.23.0.2', port=3306, user='root', password = pw, database='quant')  
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
        
        

days = loadfromMysql(code ='603618', start_date = '2015-01-01', paralist = ['Date','Open','Close','High','Low'])
days = days.sort_index()
days.index.name = 'DateTime'
daysreshape = days.reset_index()
# convert the datetime64 column in the dataframe to 'float days'
daysreshape['DateTime']=mdates.date2num(daysreshape['DateTime'].astype(dt.datetime))
daysreshape = daysreshape.reindex(columns=['DateTime','Open','High','Low','Close'])  
    
Av1 = movingaverage(daysreshape.Close.values, MA1)
Av2 = movingaverage(daysreshape.Close.values, MA2)
SP = len(daysreshape.DateTime.values[MA2-1:])
fig = plt.figure(facecolor='#07000d',figsize=(15,10))
    
ax1 = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4, axisbg='#07000d')
candlestick_ohlc(ax1, daysreshape.values[-SP:], width=.6, colorup='#ff1717', colordown='#53c156')
Label1 = str(MA1)+' SMA'
Label2 = str(MA2)+' SMA'
    
ax1.plot(daysreshape.DateTime.values[-SP:],Av1[-SP:],'#e1edf9',label=Label1, linewidth=1.5)
ax1.plot(daysreshape.DateTime.values[-SP:],Av2[-SP:],'#4ee6fd',label=Label2, linewidth=1.5)
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

 # plot an RSI indicator on top
maLeg = plt.legend(loc=9, ncol=2, prop={'size':7},
                       fancybox=True, borderaxespad=0.)
maLeg.get_frame().set_alpha(0.4)
textEd = pylab.gca().get_legend().get_texts()
pylab.setp(textEd[0:5], color = 'w')
    
ax0 = plt.subplot2grid((6,4), (0,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
rsi = rsiFunc(daysreshape.Close.values)
rsiCol = '#c1f9f7'
posCol = '#386d13'
negCol = '#8f2020'
    
ax0.plot(daysreshape.DateTime.values[-SP:], rsi[-SP:], rsiCol, linewidth=1.5)
ax0.axhline(70, color=negCol)
ax0.axhline(30, color=posCol)
ax0.fill_between(daysreshape.DateTime.values[-SP:], rsi[-SP:], 70, where=(rsi[-SP:]>=70), facecolor=negCol, edgecolor=negCol, alpha=0.5)
ax0.fill_between(daysreshape.DateTime.values[-SP:], rsi[-SP:], 30, where=(rsi[-SP:]<=30), facecolor=posCol, edgecolor=posCol, alpha=0.5)
ax0.set_yticks([30,70])
ax0.yaxis.label.set_color("w")
ax0.spines['bottom'].set_color("#5998ff")
ax0.spines['top'].set_color("#5998ff")
ax0.spines['left'].set_color("#5998ff")
ax0.spines['right'].set_color("#5998ff")
ax0.tick_params(axis='y', colors='w')
ax0.tick_params(axis='x', colors='w')
plt.ylabel('RSI')

volumeMin = 0
ax1v = ax1.twinx()
ax1v.fill_between(daysreshape.DateTime.values[-SP:],volumeMin, days.Volume.values[-SP:], facecolor='#00ffe8', alpha=.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.grid(False)
    ###Edit this to 3, so it's a bit larger
ax1v.set_ylim(0, 3*days.Volume.values.max())
ax1v.spines['bottom'].set_color("#5998ff")
ax1v.spines['top'].set_color("#5998ff")
ax1v.spines['left'].set_color("#5998ff")
ax1v.spines['right'].set_color("#5998ff")
ax1v.tick_params(axis='x', colors='w')
ax1v.tick_params(axis='y', colors='w')

