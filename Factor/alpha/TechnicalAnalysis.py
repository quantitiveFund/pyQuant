# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 19:24:23 2018

@author: Pikari
"""

from math import floor
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model
from sqlalchemy import create_engine
engine = create_engine('mysql+mysqldb://root:password@localhost:3306/database?charset=utf8')    

def get_data(stock, start_date, end_date):
    data = pd.read_sql('select * from stock_data partition(%s) \
                       where Date between "%s" and "%s"'%
                       (stock, start_date, end_date), 
                       engine, 
                       index_col='Date')
    return data

def ts_sum(data, n):
    return data.rolling(n).sum()

def ts_max(data, n):
    return data.rolling(n).max()

def ts_min(data, n):
    return data.rolling(n).min()

def ts_avedve(data, n):
    mean = data.rolling(n).mean()
    avedev = pd.Series(0, index=data.index)
    
    for i in range(n):
        avedev += abs(mean - data.shift(i))
        
    return avedev / n

def compare_max(dataframe1, dataframe2):
    dataframe1[dataframe1 < dataframe2] = dataframe2
    return dataframe1

def compare_min(dataframe1, dataframe2):
    dataframe1[dataframe1 > dataframe2] = dataframe2
    return dataframe1

def ref(data, n):
    if type(n) is int:
        return data.shift(n)
    else:
        return pd.Series([data.shift(n[i])[i] for i in range(len(n))], index=data.index)

def ma(data, n=5):
    return data.rolling(n).mean()

def sma(data, n=5, m=1):
    sma = [data[0]]
    
    for i in range(1, len(data)):
        sma.append((data[i] + sma[-1] * (n - m)) / n)
        
    return pd.Series(sma, index=data.index)

def ema(data, n=12):
    ema = [data[0]]
    
    for i in range(1, len(data)):
        ema.append(data[i] * 2 / (n + 1) + ema[-1] * (n - 1) / (n + 1))
        
    return pd.Series(ema, index=data.index)

def dma(data, weight):
    dma = [data[0]]
    
    for i in range(1, len(data)):
        dma.append(data[i] * weight[i] + dma[-1] * (1 - weight[i]))
        
    return pd.Series(dma, index=data.index)

'''
def ema(data, n=12, i=12):
    if i == 1:
        return data.shift(n-1)
    else:
        i -= 1
        return 2 / (n + 1) * data.shift(n-i-1) + (n - 1) / (n + 1) * ema(data, n, i)

def dma(data, weight):
    if len(data) == 1:
        return data[-1]
    else:
        return data[-1] * weight[-1] + dma(data[:-1], weight[:-1]) * (1 - weight[-1])
'''
class Qualification():
    def __init__(self, stock, start_date, end_date, adj=False):
        self.stock = stock
        self.start_date = start_date
        self.end_date = end_date
        
        self.data = get_data(stock, start_date, end_date)
        
        if adj == False:
            self.open = self.data.Open
            self.high = self.data.High
            self.low = self.data.Low
            self.close = self.data.Close
        
        elif adj == True:
            self.adjfactor = self.data.AdjFactor
            self.open = self.data.Open * self.adjfactor
            self.high = self.data.High * self.adjfactor
            self.low = self.data.Low * self.adjfactor
            self.close = self.data.Close * self.adjfactor
            
        self.chgrate = self.data.ChgRate
        self.chamount = self.data.ChgAmount
        self.volume = self.data.Volume
        self.turnover = self.data.Turnover
        self.mktvalue = self.data.MktValue

    def SMA(self, n=5):
        return ma(self.close, n)
    
    def EMA(self, n=12, i=12):
        if i == 1:
            return self.close.shift(n-1)
        else:
            i -= 1
            return 2 / (n + 1) * self.close.shift(n-i-1) + (n - 1) / (n + 1) * self.EMA(n, i)

    def ACCER(self, n=8):
        coef = [None] * n
        
        for i in range(n, len(self.data)):
            daily_coef = linear_model.LinearRegression().fit(np.array([[x+1] for x in range(n)]), 
                                                       self.close.iloc[i-n:i].values.reshape(-1, 1)).coef_[0, 0]
            coef.append(daily_coef / self.close[i])
            
        return pd.Series(coef, index=self.data.index)
    
    def ADTM(self, n=23, m=8):    
        dtm, dbm = pd.Series(0, index=self.data.index), pd.Series(0, index=self.data.index)
        dtm[self.open > self.open.shift(1)] = compare_max(self.high - self.open, self.open - self.open.shift(1))
        dbm[self.open < self.open.shift(1)] = compare_max(self.open - self.low, self.open - self.open.shift(1))
        stm = ts_sum(dtm, n)
        sbm = ts_sum(dbm, n)
        adtm = abs(stm - sbm) / compare_max(stm, sbm)
        adtmma = ma(adtm, m)
        return adtm, adtmma
    
    def ATR(self, n=14):
        tr = compare_max(compare_max(abs(self.high - self.low), abs(self.high - self.close.shift(1))), abs(self.close.shift(1) - self.low))
        atr = ma(tr, n)
        return tr, atr

    def BIAS(self, n1=6, n2=12, n3=24):
        bias1 = (self.close / ma(self.close, n1) - 1) * 100
        bias2 = (self.close / ma(self.close, n2) - 1) * 100
        bias3 = (self.close / ma(self.close, n3) - 1) * 100
        return bias1, bias2, bias3
    
    def BIAS_QL(self, n=6, m=6):
        bias = (self.close / ma(self.close, n) - 1) * 100
        biasma = ma(bias, m)
        return bias, biasma
    
    def BIAS36(self, m=6):
        bias36 = ma(self.close, 3) - ma(self.close, 6)
        bias612 = ma(self.close, 6) - ma(self.close, 12)
        mabias = ma(bias36, m)
        return bias36, bias612, mabias
    
    def CCI(self, n=14):
        typ = (self.close + self.high + self.low) / 3
        cci = (typ - ma(typ, n)) / ts_avedve(typ, n) / 0.015
        return cci
    
    def CYF(self, n=21):
        cyf = 100 - 100 / (1 + ema(self.turnover, n))
        return cyf
    
    def DKX(self, m=10):
        mid = (3 * self.close + self.open + self.high + self.low) / 6
        dkx = pd.Series(0, index=self.close.index)
        
        for w in range(20):
            dkx += (20 - w) * mid.shift(w) / 210
            
        madkx = ma(dkx, m)
        return dkx, madkx
    
    def MFI(self, n=14):
        typ = (self.close + self.high + self.low) / 3
        mf = typ * self.volume
        pmf, nmf = pd.Series(0, index=typ.index), pd.Series(0, index=typ.index)
        pmf[typ > typ.shift(1)] = mf
        nmf[typ < typ.shift(1)] = mf
        mfi = 100 - 100 / (1 + pmf.rolling(n).sum() / nmf.rolling(n).sum())
        return mfi
        
    def MTM(self, n=12, m=6):
        mtm = self.close - self.close.shift(n)
        mamtm =  ma(mtm, m)
        return mtm, mamtm
    
    def ROC(self, n=12, m=6):
        roc = self.close / self.close.shift(n) - 1
        maroc = ma(roc, m)
        return roc, maroc
        
    def RSI(self, n=6):
        up = pd.Series(0, index=self.close.index)
        up[self.chgrate > 0] = self.chgamount
        rsi = 100 * ma(up, n) / ma(abs(self.chgrate), n)
        return rsi
    
    def MARSI(self, m1=10, m2=6):
        marsi10 = ma(self.RSI(), m1)
        marsi6 = ma(self.RSI(), m2)
        return marsi10, marsi6
    
    def OSC(self, n=20, m=6):
        osc = (self.close - ma(self.close, n)) * 100
        maosc = ema(osc, m)
        return osc, maosc
    
    def UDL(self, n1=3, n2=5, n3=10, n4=20, m=6):
        udl = (ma(self.close, n1) + ma(self.close, n2) + ma(self.close, n3) + ma(self.close, n4)) / 4
        maudl = ma(udl, m)
        return udl, maudl
    
    def WR(self, n=10, m=6):
        wr = (ts_max(self.high, n) - self.close) / (ts_max(self.high, n) - ts_min(self.low, n)) * 100
        mawr = ma(wr, m)
        return wr, mawr
    
    def LWR(self, n=9, m1=3, m2=3):
        rsv = self.WR(n)[0]
        lwr1 = ma(rsv, m1)
        lwr2 = ma(lwr1, m2)
        return lwr1, lwr2
    
    def TAPI(self, m=6):
        pass
    
    def FSL(self):
        swl = (ema(self.close, 5) * 7 + ema(self.close, 10)) * 3 / 10
        weight = compare_max(pd.Series(1, index=self.close.index), 100 / 3 * (ts_sum(self.volume, 5)) / (self.mktvalue))
        sws = dma(ema(self.close, 12), weight)                
        return swl, sws
    
    def CHO(self, n1=10, n2=20, m=6):
        mid = (self.volume * (2 * self.close - self.high - self.low) / (self.high + self.low)).cumsum()
        cho = ma(mid, n1) - ma(mid, n2)
        macho = ma(cho, m)
        return cho, macho
    
    def CYE(self):
        var1 = ma(self.close, 5)
        var2 = ma(self.close, 20)
        s = var1 / var1.shift(1) - 1
        m = var2 / var2.shift(1) - 1
        return s, m
    #
    def DBQR(self, n=5, m1=10, m2=20, m3=60):
        zs = None
        gg = self.close / self.close.shift(n) - 1
        madbrq1 = ma(gg, m1)
        madbrq2 = ma(gg, m2)
        madbrq3 = ma(gg, m3)
        return zs, gg, madbrq1, madbrq2, madbrq3
    
    def DMA(self, n1=10, n2=50, m=10):
        ddd = ma(self.close, n1) - ma(self.close, n2)
        ama = ma(ddd, m)
        return ddd, ama
    
    def DMI(self, n=14, m=6):
        tr = ts_sum(compare_max(compare_max(self.high - self.low, abs(self.high - self.close.shift(1))), abs(self.low - self.close.shift(1))), n)
        hd = self.high.diff(1)
        ld = -self.low.diff(1)
        dmp, dmm = pd.Series(0, index=hd.index), pd.Series(0, index=hd.index)
        dmp[(hd>0) & (hd>ld)] = hd
        dmm[(ld>0) & (ld>hd)] = ld
        dmp, dmm = ts_sum(dmp, n), ts_sum(dmm, n)
        di1, di2 = dmp * 100 / tr, dmm * 100 / tr
        adx = ma(abs(di2 - di1) / (di1 + di2) * 100, m)
        adxr = (adx + adx.shift(m)) / 2
        return adx, adxr, di1, di2
    
    def DPO(self, n1=20, n2=10, m=6):
        dpo = self.close - ma(self.close, n1).shift(n2)
        madpo = ma(dpo, m)
        return dpo, madpo
        
    def EMV(self, n=14, m=9):
        vol = ma(self.volume, n) / self.volume
        mid = 100 * (self.high + self.low).diff(1) / (self.high + self.low)
        emv = ma(mid * vol * (self.high - self.low) / ma(self.high - self.low, n), n)
        maemv = ma(emv, m)
        return emv, maemv
    
    def GDX(self, n=30, m=9):
        aa = abs((2 * self.close + self.high + self.low) / 4 - ma(self.close, n)) / ma(self.close, n)
        gdx = dma(self.close, aa.fillna(0))
        rl = (1 + m / 100) * gdx
        sl = (1 - m / 100) * gdx
        return gdx, rl, sl
    
    def JLHB(self, n=7, m=5):
        jlhb = pd.Series(0, index=self.close.index)
        var1 = (self.close - ts_min(self.low, 60)) / (ts_max(self.high, 60) - ts_min(self.low, 60)) * 80
        b = sma(var1.fillna(0), n, 1)
        var2 = sma(b.fillna(0), m, 1)
        jlhb[(b > var2) & (b < 40)] = 50
        return b, var2, jlhb
    
    def JS(self, n=5, m1=5, m2=10, m3=20):
        js = 100 * self.close.diff(n) / (n * self.close.shift(n))
        majs1 = ma(js, m1)
        majs2 = ma(js, m2)
        majs3 = ma(js, m3)
        return js, majs1, majs2, majs3
    
    def MACD(self, n1=12, n2=26, m=9):
        dif = ema(self.close, n1) - ema(self.close, n2)
        dea = ema(dif, m)
        macd = 2 * (dif - dea)
        return dif, dea, macd
    
    def VMACD(self, n1=12, n2=26, m=9):
        dif = ema(self.volume, n1) - ema(self.volume, n2)
        dea = ema(dif, m)
        macd = 2 * (dif - dea)
        return dif, dea, macd
    
    def QACD(self, n1=12, n2=26, m=9):
        dif = ema(self.close, n1) - ema(self.close, n2)
        macd = ema(dif, m)
        ddif = dif - macd
        return dif, macd, ddif
    
    def TRIX(self, n=12, m=9):
        mtr = ema(ema(ema(self.close, n), n), n)
        trix = (mtr / mtr.shift(1) - 1) * 100
        matrix = ma(trix, m)
        return trix, matrix
    #
    def UOS(self, n1=7, n2=14, n3=28, m=6):
        th = compare_max(self.high, self.close.shift(1))
        tl = compare_min(self.low, self.close.shift(1))
        acc1 = ts_sum(self.close - tl, n1) / ts_sum(th - tl, n1)
        acc2 = ts_sum(self.close - tl, n2) / ts_sum(th - tl, n2)
        acc3 = ts_sum(self.close - tl, n3) / ts_sum(th - tl, n3)
        uos = (acc1 * n2 * n3 + acc2 * n1 * n3 + acc3 * n1 * n2) * 100/ (n1 * n2 + n1 * n3 + n2 * n3)
        mauos = ma(uos, m)
        return uos, mauos
    
    def VPT(self, n=51, m=6):
        vpt = ts_sum(self.volume * self.close.diff(1) / self.close.shift(1), n)
        mavpt = ma(vpt, m)
        return vpt, mavpt
    
    def WVAD(self, n=24, m=6):
        wvad = ts_sum((self.close - self.open) / (self.high - self.low) * self.volume, n) / 10000
        mawvad = ma(wvad, m)
        return wvad, mawvad
    
    def QR(self, n=21):
        pass
    
    def BRAR(self, n=26):
        zero = pd.Series(0, index=self.close.index)
        br = ts_sum(compare_max(zero, self.high - self.close.shift(1)), n) / ts_sum(compare_max(zero, self.close.shift(1) - self.low), n) * 100
        ar = ts_sum(self.high - self.open, n) / ts_sum(self.open - self.low, n) * 100
        return br, ar
    
    def CR(self, n=26, m1=10, m2=20, m3=40, m4=62):
        zero = pd.Series(0, index=self.close.index)
        mid = (self.high + self.low).shift(1) / 2
        cr = ts_sum(compare_max(zero, self.high - mid), n) / ts_sum(compare_max(zero, mid - self.low), n) * 100
        ma1 = ma(cr, m1).shift(floor(m1 / 2.5 + 1))
        ma2 = ma(cr, m2).shift(floor(m2 / 2.5 + 1))
        ma3 = ma(cr, m3).shift(floor(m3 / 2.5 + 1))
        ma4 = ma(cr, m4).shift(floor(m4 / 2.5 + 1))
        return cr, ma1, ma2, ma3, ma4
    
    def MASS(self, n1=9, n2=25, m=6):
        mass = ts_sum(ma(self.high - self.low, n1) / ma(ma(self.high - self.low, n1), n1), n2)
        mamass = ma(mass, m)
        return mass, mamass
    
    def PSY(self, n=12, m=6):
        temp = self.close.diff(1)
        temp[temp <= 0] = None
        psy = temp.rolling(n).count() / n * 100
        mapsy = ma(psy, m)
        return psy, mapsy
    #
#    def VR(self, n=26, m=6):
#        zero = pd.Series(0, index=self.close.index)
#        th_vol = zero[self.diff(1) > 0] = self.volume
#        th = ts_sum(zero[self.diff(1) > 0] = self.volume, n)
#        pass
#    
#    def WAD(self, m=30):
#        mida = self.close - compare_min(self.close.shift(1), self.low)
#        midb = pd.Series(0, index=self.close.index)
#        midb[self.close.diff(1) < 0] = self.close - compare_max(self.close.shift(1), self.high)
#        pass
    
if __name__ == '__main__':
    start_date = '2017-01-01'
    end_date = '2018-01-01'
    stock = 'stock_000002'
    q = Qualification(stock, start_date, end_date)
