# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 14:13:03 2018

@author: Pikari
"""

import pandas as pd
from sqlalchemy import create_engine
from WindPy import w
w.start()
engine = create_engine('mysql+mysqldb://root:password@localhost:3306/database?charset=utf8')    

def get_start_end_date(stock):
    start_date = pd.read_sql('select min(Date) from %s' % (stock), engine).iat[0, 0]
    end_date = pd.read_sql('select max(Date) from %s' % (stock), engine).iat[0, 0]
    return [start_date, end_date]
    
def get_wind_data(stock, data_dict, start_date, end_date):
    data = w.wsd(stock, list(data_dict.keys()), start_date, end_date)
    
    if data.ErrorCode != 0:
        date_index = [date.strftime('%Y-%m-%d') for date in data.Times]
        data = pd.DataFrame(data.Data[0], index=date_index, columns=list(data_dict.values()))
        return data

if __name__ == '__main__':
    
    stock_pool = engine.execute('select stock from date_data').fetchall()
    data_dict = {'mkt_cap_ard' : 'MktValue', 
                 'adjfactor' : 'AdjFactor'}
    error_stock = []
    
    for stock in stock_pool:
    
        date = get_start_end_date(stock[0])
        
        if stock[0][-6] == '0' or stock[0][-6] == '3':
            new_data = get_wind_data(stock[0][-6:] + '.sz', data_dict, date[0], date[1])
        
        else:
            new_data = get_wind_data(stock[0][-6:] + '.sh', data_dict, date[0], date[1])
        
        if new_data is not None:
            new_data.index = pd.to_datetime(new_data.index)
            origin_data = pd.read_sql('select * from %s' % (stock[0]), engine, index_col='Date')
            concat_data = pd.concat([origin_data, new_data], axis=1)            
            concat_data.index = pd.to_datetime(concat_data.index)
            concat_data.fillna(method='backfill', inplace=True)
            concat_data.reset_index(inplace=True)
            concat_data.rename(columns={'index' : 'Date'}, inplace=True)
            concat_data.to_sql(stock[0], engine, if_exists='replace', index=False)
            print(stock[0] + ' mission complete')
        
        else:
            error_stock.append(stock[0])
            print(stock[0] + ' error founded')

'''
pd.to_sql()该方法导入的数据在进行不同数据库间传输时会报错invalid default value for
报错原因：导入过程中自动设置默认值为empty string，高版本mysql禁止使用该默认值
解决方法：
1.对默认值为empty string的列删除其默认值
alter table table_name alter column column_name drop default
2.高版本mysql须修改配置文件，未实现
'''
           
'''
数据库内存在问题的股票
现已发现的问题：
1.非股票代码
2.退市股票
3.截止至2018-04-27未上市股票
error_stock = ['stock_300361','stock_300646','stock_300728','stock_600002',
'stock_600349','stock_601206','stock_603302','stock_603587','stock_603897',
'stock_001965','stock_002920','stock_002921','stock_002922','stock_002923',
'stock_002925','stock_002926','stock_002927','stock_002928','stock_002930',
'stock_002931','stock_300504','stock_300624','stock_300634','stock_300644',
'stock_300664','stock_300684','stock_300733','stock_300735','stock_300736',
'stock_300737','stock_300738','stock_300739','stock_300740','stock_300741',
'stock_300742','stock_300743','stock_600849','stock_600901','stock_600929',
'stock_601360','stock_601828','stock_601838','stock_603056','stock_603059',
'stock_603080','stock_603156','stock_603214','stock_603283','stock_603301',
'stock_603329','stock_603348','stock_603356','stock_603506','stock_603516',
'stock_603596','stock_603655','stock_603709','stock_603712','stock_603733',
'stock_603773','stock_603871','stock_603876','stock_603895']
'''

'''
删除指定位置的数据，删除指定列
for stock in stock_pool:
    engine.execute('delete from %s where Date = "2018-06-12 00:00:00"' % (stock[0]))
    engine.execute('alter table %s drop column MktValue' % (stock[0]))
'''

'''
将某一列转化为第一列
engine.execute('alter table test modify Code text first')
条件取值
data = pd.read_sql('select * from test where Code in (stock_000002, stock_000830)', engine)
'''

'''
将所有股票导入至一张表内，并添加股票代码Code列，分区代码IntCode列
stock_code = [stock[0] for stock in stock_pool if stock[0] not in error_stock]

for stock in stock_code:
    data = pd.read_sql('select * from %s' % (stock), engine)
    data['Code'] = stock
    data['IntCode'] = int(stock[-6:])
    data.to_sql('stock_data', engine, if_exists='append', index=False)
    print(stock + ' mission complete')
'''

'''
stock_data表内数据量大，读取效率很低，每次读取都须遍历一次
解决方法：对表进行分区，按照股票分割
注意：
1.老版本mysql只支持1024个分区，新版本为8196，学校服务器为老版本，按照股票分区不可行
2.有多种分区方式，其中range和list分区方法值必须为int
alter table stock_data partition by list(IntCode) (
                partition stock_000001 values in (000001), 
                partition stock_000002 values in (000002))
'''

'''
设置分区，区块太多，暂时未找到比较合适的代码生成方案
engine = create_engine('mysql+mysqldb://root:password@localhost:3306/database?charset=utf8')    
sql = ''
for stock in stock_code:
    sql += 'partition ' + stock + ' values in (' + stock[-6:] + '), '
sql = sql[:-2]
sql = 'alter table stock_data partition by list(IntCode) ' + '(' + sql + ')'
engine.execute(sql)

读取方法
data = pd.read_sql('select * from stock_data partition(stock_000001)', engine)
'''