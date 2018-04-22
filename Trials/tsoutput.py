import tushare as ts
import pandas as pd
from datetime import *

global df
df = ts.get_stock_basics()

for i in range(0, len(df)):
        code = df.ix[i].name
        date = df.ix[str(code)]['timeToMarket']
        ipo = datetime.strptime(str(date), '%Y%m%d')
        data = ts.get_k_data(str(code), start=str(ipo), end=str(datetime.now()))
        filename = str(code) + '.csv'
        data.to_csv('C:\Python36\data\output\\' + filename, index=False)
