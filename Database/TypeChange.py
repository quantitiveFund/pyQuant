# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 20:31:32 2018

@author: Pikari
"""
#def pwd_input(msg = ''):  
#    import msvcrt, sys  
#    if msg != '':  
#        sys.stdout.write(msg)  
#    chars = []  
#    while True:  
#        newChar = msvcrt.getch()  
#        if newChar in '\3\r\n': # 如果是换行，Ctrl+C，则输入结束  
#            print('')  
#            if newChar in '\3': # 如果是Ctrl+C，则将输入清空，返回空字符串  
#                chars = []  
#            break  
#        elif newChar == '\b': # 如果是退格，则删除末尾一位  
#            if chars:  
#                del chars[-1]  
#                sys.stdout.write('\b \b') # 左移一位，用空格抹掉星号，再退格  
#        else:  
#            chars.append(newChar)  
#            sys.stdout.write('*') # 显示为星号  
#    return ''.join(chars) 

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
hostname = input('Enter the host name: ')
pw = input('Enter the password: ')
try:
    conn = mysql.connector.connect(host = hostname , user='root', password = pw , database='quant')
    cursor = conn.cursor()
except:
    print('Wrong host name or password!')    

columns_1 = ['ChgRate', 'ChgAmount', 'Swing']
columns_2 = ['Open', 'High', 'Low', 'Close', 'ChgAmount', 'ChgRate', 'Volume', 'VolTrans', 'Swing', 'Turnover']
origin_data = '--'
target_data = 'null'
target_type = 'float'

cursor.execute('show tables')
tables = cursor.fetchall()
    
for table_name in tables[2:]:
    replace_data(table_name[0], columns_1, origin_data, target_data)
    table_type_change(table_name[0], columns_2, target_type)

