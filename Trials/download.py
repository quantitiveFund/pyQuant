import numpy as np

import pandas as pd
import tushare as ts
from datetime import *
df=ts.get_stock_basics()
for i in range(len(df)):
    code=df.index[i]
    date=df.ix[code]['timeToMarket']#numpy格式#
    date=pd.to_datetime(date,format='%Y%m%d')+timedelta(-1)#timestamp格式且往前推一天(使包括ipo)#
    data=ts.get_k_data(code,start=str(date))#格式必须满足start='2015-04-22'字符串#
    data.to_csv(code+'.csv',index=False)
