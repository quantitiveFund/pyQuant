
import pandas as pd
import tushare as ts
import datetime as dt

def updatestockinfo(filelocation):
    df = ts.get_stock_basics()  # 股票基础信息 利用股票代码和IPO的时间
    for i in range(0, len(df)):
        try:
            ds = pd.read_csv(filelocation+df.ix[i].name+'.csv')
            if ds.ix[len(ds)-1].date != dt.datetime.now().strftime('%Y-%m-%d'): # 数据不是最新
                tmp = ts.get_k_data(df.ix[i].name,start=ds.ix[len(ds)-1].date, end=dt.datetime.now().strftime('%Y-%m-%d'))
                ds = pd.concat([tmp, ds], axis = 0)
                ds.to_csv(filelocation+df.ix[i].name+'.csv',columns=['date','open','high','low','close','volume'], index=False)
        except FileNotFoundError:
            ds = getnewstockinfo(i,df)
        

def getnewstockinfo(i, df):
    datafile = pd.DataFrame()  # 更新数据仓库
    try:
        startdate = str(df['timeToMarket'][i])  # 提取IPO的时间
        end_end=end_start=dt.datetime.now()  # 当前时间
 # Tushare 无法一次提取大量的信息，暂时以3000日为限，每3000日提取一次，每次提取从end_start 到 end_end。
        while int((end_end - dt.timedelta(days = 3000)).strftime('%Y%m%d')) > int(startdate):
            end_start = end_end - dt.timedelta(days = 3000)
            datafile = pd.concat([ts.get_k_data(df.ix[i].name,start=end_start.strftime('%Y%m%d'), end=end_end.strftime('%Y%m%d')), datafile], axis = 0) # 取数
            end_end = end_start
            
        end_start = startdate   # 如果太早则使用该股票的IPO日子
        datafile = pd.concat([ts.get_k_data(df.ix[i].name,start=end_start, end=end_end.strftime('%Y%m%d')), datafile], axis = 0)
    except OverflowError:
        print('股票'+df.ix[i].name+'记录异常！')
    else:
        datafile.to_csv(filelocation+df.ix[i].name+'.csv',columns=['date','open','high','low','close','volume'], index=False)  # 存储
   
        
if __name__=='__main__':  
    filelocation = 'E:/Research/Data/Tushare/temp02/'
    updatestockinfo(filelocation)
