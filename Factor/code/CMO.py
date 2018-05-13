# -*- coding: utf-8 -*-
"""
Created on Thu May 10 20:32:12 2018

@author: FY
"""

import mysql.connector
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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
aba = loadfromMysql(code = '603618', start_date ='2015-01-01', paralist = ['Date','Open','Close','High','Low','Volume'])
def MACMO(data,n):
    data.index=pd.to_datetime(data.index)
    data = data.reset_index()  #重设index
    aaa=data[['Date','Close']]
    df=pd.DataFrame(aaa,columns = ["Date","Close","up","down","Su","Sd"])
    CMO=pd.Series(0.0,index=data.Date)
    for i in range(1,len(data)):
        diff=data['Close'][i]-data['Close'][i-1]
        if diff >= 0:
            df['up'][i]=diff
            df['down'][i]=0
        else:
            df['up'][i]=0
            df['down'][i]=-diff
        df['Su'][i]=np.sum(df['up'][:i+1])  #b=np.sum(df['Close'][:5])将01234行的加和
        df['Sd'][i]=np.sum(df['down'][:i+1])                                                                                                                                                                                                                                                                                                                                                                                                                              
        CMO[i]=100*(df['Su'][i]-df['Sd'][i])/(df['Su'][i]+df['Sd'][i])                     #CMO:(SU-SD)/(SU+SD)*100;
    MACMO=pd.rolling_mean(CMO,n)   #计算简单CMO算术移动平均线MA  
    return  MACMO
MACMO=MACMO(aba,5)
#画图
plt.plot(MACMO,color='r')
  
        

