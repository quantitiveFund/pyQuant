# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 20:18:15 2018

@author: Ni He
"""

import mysql.connector
import pandas as pd
import time

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




#### 函数输入部分
#code = '600000'
#start_date = '2017-05-01'
#end_date = '2018-03-05'
##paralist = ['Date','Open','High','Low','Close','ChgAmount',\
##            'ChgRate','Volume','VolTrans','Swing','Turnover']
#paralist = ['Date','Close']
####
