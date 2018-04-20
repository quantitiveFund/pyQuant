# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 20:14:19 2018

@author: Pikari
"""

import mysql.connector
import pandas as pd
from datetime import *
from WindPy import w
import time
w.start()

def create(code):
    data = w.wsd(code, d, 'ipo')
    data = pd.DataFrame(data.Data, index=data.Fields, columns=data.Times).T
    cursor.execute('drop table if exists stock_' + code[:6])
    te = 'create table ' + 'stock_' + code[:6] + ' (\
    Date text null, \
    Open text null, \
    High text null, \
    Low text null, \
    Close text null, \
    ChgAmount text null, \
    ChgRate text null, \
    Volume text null, \
    VolTrans text null, \
    Swing text null, \
    Turnover text null)'
    cursor.execute(te)
                                     
    for i in range(1, len(data)+1):
        temp = [str(data.index[i-1]), str(data.OPEN[i-1]), str(data.HIGH[i-1]), str(data.LOW[i-1]), str(data.CLOSE[i-1]), str(data.CHG[i-1]), str(round(data.PCT_CHG[i-1], 2)), str(round(data.VOLUME[i-1]/100, 0)), str(round(data.AMT[i-1]/10000, 0)), str(round(data.SWING[i-1], 2)), str(round(data.TURN[i-1], 2))]
        sql = 'insert into ' + 'stock_' + code[:6] + ' (Date, Open, High, Low, Close, ChgAmount, ChgRate, Volume, VolTrans, Swing, Turnover) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, temp)
        
    conn.commit()
    print('Stock '+code+' has been created and stored... in %d sec.' % (time.time()-time_start))
    
    
def update(code):
    try:
        cursor.execute('select Date from ' + 'stock_' + code[:6] + ' order by Date desc limit 1')
        old_date = cursor.fetchall()[0][0]
        
        if old_date != str(datetime.now().date()):
            data = w.wsd(code, d, str(datetime.strptime(old_date, '%Y-%m-%d') + timedelta(days=1)), str(datetime.now()))
            if data.Data[0] != ['CWSDService: Parameter Error(reported from Server).']:
                data = pd.DataFrame(data.Data, index=data.Fields, columns=data.Times).T
                for i in range(1, len(data)+1):
                    temp = [str(data.index[i-1]), str(data.OPEN[i-1]), str(data.HIGH[i-1]), str(data.LOW[i-1]), str(data.CLOSE[i-1]), str(data.CHG[i-1]), str(round(data.PCT_CHG[i-1], 2)), str(int(round(data.VOLUME[i-1]/100, 0))), str(round(data.AMT[i-1]/10000, 0)), str(round(data.SWING[i-1], 2)), str(round(data.TURN[i-1], 2))]
                    sql = 'insert into ' + 'stock_' + code[:6] + ' (Date, Open, High, Low, Close, ChgAmount, ChgRate, Volume, VolTrans, Swing, Turnover) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                    cursor.execute(sql, temp)
        
        conn.commit()
        print('Stock '+code+' has been updated... in %d sec.' % (time.time()-time_start))
    except:
        create(code)

conn = mysql.connector.connect(host='localhost', port=3306, user='root', password='11031103', database='quant_backup')  
cursor = conn.cursor()

code_list = w.wset("SectorConstituent","sectorId=a001010100000000;field=wind_code").Data[0]
global d
d = ["open, high, low, close, chg, pct_chg, volume, amt, swing, turn"]

for code in code_list:
    time_start = time.time()
    update(code)

conn.close()
