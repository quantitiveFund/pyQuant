# -*- coding: utf-8 -*-
"""
Created on Thu May 31 21:25:50 2018

@author: Ni He
"""

import tushare as ts
import mysql.connector
from sqlalchemy import create_engine
import pandas as pd
import re
import io 
from pandas.io import sql

def table_exist(tab_name):
    cur.execute('show tables')  # 罗列所有当前库里面的所有表格
    tables = cur.fetchall()
    selectab = re.compile(r'\w*\w*')
    tabnames = selectab.findall(str(tables))
    res = tab_name in tabnames
    return res

stk_concept_class = ts.get_concept_classified()
stk_area_class = ts.get_area_classified()
stk_sme_class = ts.get_sme_classified()
stk_gem_class = ts.get_gem_classified()
stk_st_class = ts.get_st_classified()
stk_hs300_class = ts.get_hs300s()
stk_sz50_class = ts.get_sz50s()
stk_zz500_class = ts.get_zz500s()
stk_terminated_class = ts.get_terminated()
stk_sus_class = ts.get_suspended()


while True:
    #hostname = input('Please enter the hostname: ')
    pw = input('Please enter the password: ')
    dbname = input('Please enter the number of datebase: ')
    try:
        conn = mysql.connector.connect(host='10.23.0.2', port=3306, user='root', password=pw, database=dbname)  
        cur = conn.cursor()
        break
    except:
        re_try = input('The password might be wrong, or the datebase is not available, do you want to retry (y/n)? ')
        if re_try == 'n' or re_try == 'no':
            break
# pip install mysqlclient
# 或者 pip install pymysql 相应改成   create_engine('mysql+pymysql://root...  也可以    
conn = create_engine('mysql+mysqldb://root:11031103@10.23.0.2:3306/quant_cs?charset=utf8')
stk_concept_class.to_sql('concept', con = conn, index=True, index_label='id', if_exists = 'append')
stk_area_class.to_sql('area', con = conn, index=True, index_label='id', if_exists = 'append')
stk_sme_class.to_sql('sme', con = conn, index=True, index_label='id', if_exists = 'append')
stk_hs300_class.to_sql('hs300', con = conn, index=True, index_label='id', if_exists = 'append')
stk_sz50_class.to_sql('sz50', con = conn, index=True, index_label='id', if_exists = 'append')
stk_zz500_class.to_sql('zz500', con = conn, index=True, index_label='id', if_exists = 'append')
stk_terminated_class.to_sql('terminated', con = conn, index=True, index_label='id', if_exists = 'append')
stk_sus_class.to_sql('sus', con = conn, index=True, index_label='id', if_exists = 'append')
stk_gem_class.to_sql('gem', con = conn, index=True, index_label='id', if_exists = 'append')

#if not table_exist('concept'):
#    sql_create = 'create table concept (id int unsigned auto_increment primary key, \
#        code varchar(50) null, name varchar(50) null, concept varchar(50) null)'
#    cur.execute(sql_create)
#    conn.commit()
 


    