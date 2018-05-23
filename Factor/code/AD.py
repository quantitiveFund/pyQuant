# -*- coding: utf-8 -*-
"""
Created on Wed May 23 18:46:41 2018

@author: FY
"""
#Accumulation/Distribution (AD)集散指标

import mysql.connector
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
def loadfromMysql(code, start_date, end_date=time.strftime('%Y-%m-%d',time.localtime(time.time())), paralist = ['Date','Close']):  #time中localtime为格式化时间戳为本地的时间，time()函数可以获取当前的时间，strftime('%Y-%m-%d',为转化为年-月-日
    #连接MySQL数据库
    while True: 
        hostname = '10.23.0.2'
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
        cur.execute(sql)   #建表
        res = cur.fetchall()
        dat = pd.DataFrame(res, columns = paralist)
        dat = dat.set_index('Date')
        conn.close()
        return dat
    except:
        print('Error: unable to fetch data. You might enter a wrong code')
aba= loadfromMysql(code = '603618', start_date ='2015-01-01', paralist = ['Date','Open','Close','High','Low','Volume'])        
def AD(data):
    data.index=pd.to_datetime(data.index)    #转化为时间
    data=data.reset_index()        #重设index
    data=pd.DataFrame(data,columns=['Date','Open','Close','High','Low','Volume','constant'])
    AD=pd.Series(0.0,index=data.Date)
    for i in range(1,len(data)):
        data['constant'][0]=(2*data['Close'][0]-data['Low'][0]-data['High'][0])/(data['High'][0]-data['Close'][0]+np.e**(-10))
        data['constant'][i]=(2*data['Close'][i]-data['Low'][i]-data['High'][i])/(data['High'][i]-data['Close'][i]+np.e**(-10))    #防止分母为0
        #是否需要避免high=close但是close！=low的情况
        AD[0]=0
        AD[i]=AD[i-1]+(data['constant'][i]*data['Volume'][i])
    return AD
AD=AD(aba)
plt.plot(AD,color='r')
















