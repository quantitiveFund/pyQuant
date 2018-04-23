# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 20:31:32 2018

@author: Pikari
"""

def replace_data(table_name, columns, origin_data, target_data):
    try:
        for i in range(len(columns)):
            cursor.execute('update %s set %s = %s where %s = "%s"'%(table_name, columns[i], target_data, columns[i], origin_data))
            conn.commit()
        print('\033[0;32m' + table_name + ' replacing compete' + '\033[0m')
    except:
        print('\033[0;31m' + table_name + ' no need to replace' + '\033[0m')

def table_type_change(table_name, columns, target_type):
    try:
        for i in range(len(columns)):
            cursor.execute('alter table %s modify %s %s'%(table_name, columns[i], target_type))
        print('\033[0;32m' + table_name + ' type changing compete' + '\033[0m')
    except:
        print('\033[0;31m' + table_name + ' no need to change' + '\033[0m')

import mysql.connector
conn = mysql.connector.connect(host='******', user='root', password='******', database='quant')
cursor = conn.cursor()

columns_1 = ['ChgRate', 'ChgAmount', 'Swing']
columns_2 = ['Open', 'High', 'Low', 'Close', 'ChgAmount', 'ChgRate', 'Volume', 'VolTrans', 'Swing', 'Turnover']
origin_data = '--'
target_data = 'null'
target_type = 'float'

cursor.execute('show tables')
tables = cursor.fetchall()
    
for table_name in tables[4:20]:
    replace_data(table_name[0], columns_1, origin_data, target_data)
    table_type_change(table_name[0], columns_2, target_type)
