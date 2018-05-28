# -*- coding: utf-8 -*-
"""
Created on Thu May  3 00:20:58 2018

@author: Pikari
"""

import pandas as pd
import numpy as np
import mysql.connector

conn = mysql.connector.connect(host='????', user='root', password='????', database='quant')
cursor = conn.cursor()

cursor.execute('show tables')
tables = cursor.fetchall()
stock_code_list = pd.DataFrame(tables)
stock_pool = list(stock_code_list.iloc[-50:, 0])
date = '2017-01-04'

def get_trade_date(date, lag):
    data = pd.read_sql('select * from stock_000001', conn)
    target_date = data[data.index[data.Date.isin([date])][0] - lag:data.index[data.Date.isin([date])][0] + 1]
    return list(target_date.Date)

def get_panel_data(stock_pool, target_data, date, lag=20):
    panel_data = pd.Series()
    date_list = get_trade_date(date, lag)
    for stock_code in stock_pool:
        time_series_data = pd.read_sql('select %s, %s from %s where Date between "%s" and "%s"'%(target_data, 'Date', stock_code, date_list[0], date), conn, index_col='Date')
        time_series_data.columns = [stock_code]
        panel_data = pd.concat([panel_data, time_series_data], axis=1)
    panel_data.drop(panel_data.columns[0], axis=1, inplace=True)
    return panel_data.dropna(axis=1)

def delta(panel_data, lag):
    return panel_data.diff(lag)

def delay(panel_data, lag):
    return panel_data.shift(lag)

def standard_rank(panel_data):
    return panel_data.rank(axis=1, pct=True)
 
def correlation(panel_data_1, panel_data_2, day):
    return panel_data_1.rolling(day).corr(panel_data_2)

def covariance(panel_data_1, panel_data_2, day):
    return panel_data_1.rolling(day).cov(panel_data_2)

def ts_sum(panel_data, day):
    return panel_data.rolling(day).sum()

def scale(panel_data, a=1):
    return (a * panel_data.T / abs(panel_data).sum(axis=1)).T

def signedpower(panel_data, power):
    return pow(panel_data, power)

def ts_rank(panel_data, day):
    return panel_data.rolling(day).apply(lambda x : pd.Series(x).rank(pct=True)[day-1])

def decay_linear(panel_data, day):
    weight = (1 + day) * day / 2
    weighted_moving_average = pd.DataFrame(index=panel_data.index, columns=panel_data.columns).fillna(0)
    for i in range(day):
        weighted_moving_average += panel_data.shift(i) * (i + 1) / weight
    return weighted_moving_average

def ts_min(panel_data, day):
    return panel_data.rolling(day).min()

def ts_max(panel_data, day):
    return panel_data.rolling(day).max()

def ts_argmin(panel_data, day):
    return day - 1 - panel_data.rolling(day).apply(np.argmin)

def ts_argmax(panel_data, day):
    return day - 1 - panel_data.rolling(day).apply(np.argmax)

def product(panel_data, day):
    return panel_data.rolling(day).mul()

def stddev(panel_data, day):
    return panel_data.rolling(day).std()

def ad(panel_data, day):
    return panel_data.rolling(day).mean()

def compare_max(panel_data_1, panel_data_2):
    panel_data_1[panel_data_1 < panel_data_2] = panel_data_2
    return panel_data_1

def compare_min(panel_data_1, panel_data_2):
    panel_data_1[panel_data_1 > panel_data_2] = panel_data_2
    return panel_data_1

open = get_panel_data(stock_pool, 'Open', date, lag=250)
high = get_panel_data(stock_pool, 'High', date, lag=250)
low = get_panel_data(stock_pool, 'Low', date, lag=250)
close = get_panel_data(stock_pool, 'Close', date, lag=250)
returns = get_panel_data(stock_pool, 'ChgRate', date, lag=250)
volume = get_panel_data(stock_pool, 'Volume', date, lag=250)
vwap = (open + high + low + close) / 4
cap = close * volume

class Alpha(object):
    def __init__(self, open, high, low, close, returns, volume, vwap):
        self.open = open
        self.high = high
        self.close = close
        self.returns = returns
        self.volume = volume
        self.vwap = vwap

    def alpha_002(self):
        return -1 * correlation(standard_rank(delta(np.log(self.volume), 2)), standard_rank((self.close / self.open - 1)), 6)
    
    def alpha_003(self):
        return -1 * correlation(standard_rank(self.open), standard_rank(self.volume), 10)
    
    def alpha_004(self):
        return -1 * ts_rank(standard_rank(self.low), 9)
    
    def alpha_005(self):
        return standard_rank(self.open - ts_sum(vwap, 10) / 10) * (-1 * abs(standard_rank(self.close - self.vwap)))
    
    def alpha_006(self):
        return -1 * correlation(self.open, self.volume, 10)
    
    def alpha_007(self):
        alpha_007 = pd.DataFrame(index=self.close.index, columns=self.close.columns)
        alpha_007[self.volume.rolling(5).mean() < self.volume] = -1 * ts_rank(abs(delta(self.close, 5)), 5) * np.sign((delta(self.close, 5)))
        alpha_007[self.volume.rolling(5).mean() >= self.volume] = -1
        return alpha_007
        
    def alpha_008(self):
        return -1 * standard_rank((ts_sum(self.open, 5) * ts_sum(self.returns, 5)) - delay(ts_sum(self.open, 5) * ts_sum(self.returns, 5), 10))
    
    def alpha_009(self):
        alpha_009 = pd.DataFrame(index=self.close.index, columns=self.close.columns)
        judgement_1 = 0 < ts_min(delta(self.close, 1), 5)
        judgement_2 = 0 > ts_max(delta(self.close, 1), 5)
        alpha_009 = -delta(self.close, 1)
        alpha_009[judgement_1 | judgement_2] = delta(self.close, 1)
        return alpha_009
    
    def alpha_010(self):
        alpha_010 = pd.DataFrame(index=self.close.index, columns=self.close.columns)
        judgement_1 = 0 < ts_min(delta(self.close, 1), 4)
        judgement_2 = 0 > ts_max(delta(self.close, 1), 4)
        alpha_010 = standard_rank(-delta(self.close, 1))
        alpha_010[judgement_1 | judgement_2] = standard_rank(delta(self.close, 1))
          
    def alpha_011(self):
        return (standard_rank(ts_max(self.vwap - self.close, 3)) + standard_rank(ts_min(self.vwap - self.close, 3))) * standard_rank(delta(self.volume, 3))
    
    def alpha_012(self):
        return np.sign(delta(self.volume, 1)) * (-1 * delta(self.close, 1))
    
    def alpha_013(self):
        return -1 * standard_rank(covariance(standard_rank(self.close), standard_rank(self.volume), 5))
    
    def alpha_014(self):
        return -1 * standard_rank(delta(self.returns, 3)) * correlation(self.open, self.volume, 10)
    
    def alpha_015(self):
        return -1 * ts_sum(standard_rank(correlation(standard_rank(self.high), standard_rank(self.volume), 3)), 3)
    
    def alpha_016(self):
        return -1 * standard_rank(correlation(standard_rank(self.high), standard_rank(self.volume), 5))
    
    def alpha_017(self):
        return -1 * standard_rank(ts_rank(self.close, 10)) * standard_rank(delta(delta(self.close, 1), 1)) * standard_rank(ts_rank(self.volume / self.volume.rolling(20).mean(), 5))
    
    def alpha_018(self):
        return -1 * standard_rank(stddev(abs(self.close - self.open), 5) + self.close - self.open + correlation(self.close, self.open, 10))
    
    def alpha_019(self):
        return -1 * np.sign(close - delay(self.close, 7) + delta(self.close, 7)) * (1 + standard_rank(1 + ts_sum(self.returns, 5)))
    
    def alpha_020(self):
        return -1 * standard_rank(self.open - delay(self.high, 1)) * standard_rank(self.open - delay(self.lose, 1)) * standard_rank(self.open - delay(self.low, 1))
    
    def alpha_021(self):
        alpha_021 = pd.DataFrame(index=self.close.index, columns=self.close.columns)
        judgement_1 = ts_sum(self.close, 8) / 8 + stddev(self.close, 8) < ts_sum(self.close, 2) / 2
        judgement_2 = ts_sum(self.close, 2) / 2 - stddev(self.close, 8) > ts_sum(self.close, 2) / 2
        judgement_3 = 1 <= self.volume / self.volume.rolling(20).mean()
        alpha_021 = alpha_021.fillna(-1)
        alpha_021[judgement_1] = 1
        alpha_021[judgement_2 | judgement_3] = 1
        return alpha_021
    
    def alpha_022(self):
        return -1 * delta(correlation(self.high, self.volume, 5), 5) * standard_rank(stddev(self.close, 20))
    
    def alpha_023(self):
        alpha_023 = pd.DataFrame(index=self.high.index, columns=self.high.columns)
        alpha_023[ts_sum(self.high, 20) / 20 < self.high] = -1 * delta(self.high, 2)
        alpha_023[ts_sum(self.high, 20) / 20 >= self.high] = 0
        return alpha_023
    
    def alpha_024(self):
        alpha_024 = -1 * delta(self.close, 3)
        judgement = (delta(ts_sum(self.close, 100) / 100, 100) / delay(self.close, 100) <= 0.05)
        alpha_024[judgement] = -1 * (self.close - ts_min(self.close, 100))
        return alpha_024
    
    def alpha_025(self):
        return standard_rank(-1 * self.returns * self.volume.rolling(5).mean() * self.vwap * (self.high - self.close))
    
    def alpha_026(self):
        return -1 * ts_max(correlation(ts_rank(self.volume, 5), ts_rank(self.high, 5), 5), 3)
    
    def alpha_027(self):
        alpha_027 = pd.DataFrame(index=self.close.index, columns=self.close.columns)
        alpha_027[0.5 < standard_rank(ts_sum(correlation(standard_rank(self.volume), standard_rank(self.vwap), 6), 2) / 2)] = -1
        return alpha_027.fillna(1)
        
    def alpha_028(self):
        return scale(correlation(self.volume.rolling(20).mean(), self.low, 5) + (self.high + self.low) / 2 - self.close)
    
    def alpha_029(self):
        return ts_min(product(standard_rank(standard_rank(scale(np.log(ts_sum(ts_min(standard_rank(standard_rank(-1 * standard_rank(delta(close - 1, 5)))), 2), 1))))), 1), 5) + ts_rank(delay(-1 * returns, 6), 5)
    
    def alpha_030(self):
        return (1 - standard_rank(np.sign(self.close - delay(self.close, 1)) + np.sign(delay(self.close, 1) - delay(self.close, 2)) + np.sign(delay(self.close, 2) - delay(self.close, 3)))) * ts_sum(self.volume, 5) / ts_sum(self.volume, 20)
    
    def alpha_031(self):
        return standard_rank(standard_rank(standard_rank(decay_linear(-1 * standard_rank(standard_rank(delta(self.close, 10))), 10)))) + standard_rank(-1 * delta(self.close, 3)) + np.sign(scale(correlation(self.volume.rolling(20).mean(), self.low, 12)))
    
    def alpha_032(self):
        return scale(ts_sum(self.close, 7) / 7 - self.close) + 20 * scale(correlation(self.vwap, delay(self.close, 5), 230))
    
    def alpha_033(self):
        return standard_rank(-1 * (1 - self.open / self.close))
    
    def alpha_034(self):
        return standard_rank(1 - standard_rank(stddev(self.returns, 2) / stddev(self.returns, 5)) + 1 - standard_rank(delta(self.close, 1)))
    
    def alpha_035(self):
        return ts_rank(self.volume, 32) * (1 - ts_rank(self.close + self.high - self.low), 16) * (1 - ts_rank(self.returns, 32))
    
    def alpha_036(self):
        return 2.21 * standard_rank(correlation(self.close - self.open, delay(self.volume, 1), 15)) + 0.7 * standard_rank(self.open - self.close) + 0.73 * standard_rank(ts_rank(delay(-1 * self.returns, 6), 5)) + standard_rank(abs(correlation(self.vwap, self.volume.rolling(20).mean(), 6))) + 0.6 * standard_rank((ts_sum(self.close, 200) / 200 - self.open) * (self.close - self.open)) 
    
    def alpha_037(self):
        return standard_rank(correlation(delay(self.open - self.close, 1), self.close, 5)) + standard_rank(self.open - self.close)
    
    def alpha_038(self):
        return -1 * standard_rank(ts_rank(self.close, 10)) * standard_rank(self.close / self.open)
    
    def alpha_039(self):
        return -1 * standard_rank(delta(self.close, 7) * (1 - standard_rank(decay_linear(self.volume / self.volume.rolling(20).mean(), 9)))) * (1 + standard_rank(ts_sum(self.returns, 250)))
       
    def alpha_040(self):
        return -1 * standard_rank(stddev(self.high, 10)) * correlation(self.high, self.volume, 10)    
    
    def alpha_041(self):
        return pow(self.high * self.low, 0.5) * self.vwap
    
    def alpha_042(self):
        return standard_rank(self.vwap - self.close) / standard_rank(self.vwap + self.close)
    
    def alpha_043(self):
        return ts_rank(self.volume / self.volume.rolling(20).mean, 20) * ts_rank(-1 * delta(self.close, 7), 8)
    
    def alpha_044(self):
        return -1 * correlation(self.high, standard_rank(self.volume), 5)
    
    def alpha_045(self):
        return -1 * standard_rank(ts_sum(delay(self.close, 5), 20) / 20) * correlation(self.close, self.volume, 2) * standard_rank(correlation(ts_sum(self.close, 5), ts_sum(self.close, 20), 2))
    
    def alpha_050(self):
        return -1 * ts_max(standard_rank(correlation(standard_rank(self.volume), standard_rank(self.vwap), 5)), 5)
    
    def alpha_051(self):
        alpha_051 = -1 * (self.close - delay(self.close, 1))
        judgement = delay(self.close, 20) - delay(self.close, 10) / 10 - (delay(self.close, 10) - self.close) / 10 < -0.05
        alpha_051[judgement] = 1
        return alpha_051
    
    def alpha_052(self):
        return (-1 * ts_min(self.low, 5) + delay(ts_min(self.low, 5), 5)) * standard_rank(ts_sum(self.returns, 240) - ts_sum(self.returns, 20) / 220) * ts_rank(self.volume, 5)
    
    def alpha_053(self):
        return -1 * delta(((self.close - self.low) - (self.high - self.close)) / (self.close - self.low), 9)
    
    def alpha_054(self):
        return -1 * ((self.low - self.close) * pow(self.open, 5)) / ((self.low - self.high) * pow(self.close, 5))
    
    def alpha_055(self):
        return -1 * correlation(standard_rank((self.close - ts_min(self.low, 12)) / (ts_max(self.high, 12) - ts_min(self.low, 12))), standard_rank(self.volume), 6)
    
    def alpha_056(self):
        return -1 * standard_rank(ts_sum(self.returns, 10) / ts_sum(ts_sum(self.returns, 2), 3)) * standard_rank(self.returns * self.cap)
    
    def alpha_057(self):
        return -1 * (self.close - self.vwap) / decay_linear(standard_rank(ts_argmax(self.close, 30)), 2)
    
    def alpha_058(self):
        pass
    
    def alpha_059(self):
        pass
    
    def alpha_060(self):
        return -1 * 2 * scale(standard_rank((2 * self.close - self.low - self.high) / (self.high - self.low) * self.volume) - scale(standard_rank(ts_argmax(self.close, 10))))
    
    def alpha_061(self):
        alpha_061 = pd.DataFrame(-np.ones_like(self.close), index=self.close.index, columns=self.close.columns)
        judgement = (standard_rank(self.vwap - ts_min(self.vwap, 16))) < (standard_rank(correlation(self.vwap, self.volume.rolling(180).mean(), 17)))
        alpha_061[judgement] = 1
        return alpha_061
    
    def alpha_062(self):
        alpha_062 = pd.DataFrame(-np.ones_like(self.close), index=self.close.index, columns=self.close.columns)
        judgement_1 = (standard_rank(correlation(self.vwap, ts_sum(self.volume.rolling(20).mean(), 22), 9))) < (standard_rank(standard_rank(self.open) * 2))
        judgement_2 = (standard_rank(standard_rank(self.open) * 2)) < (-1 * (standard_rank((self.high + self.low) / 2 + standard_rank(self.high))))
        alpha_062[judgement_1 & judgement_2] = 1
        return  alpha_062
    
    def alpha_063(self):
        pass
    
    def alpha_064(self):
        alpha_064 = pd.DataFrame(-np.ones_like(self.close), index=self.close.index, columns=self.close.columns)
        judgement = (standard_rank(correlation(ts_sum(self.open * 0.178404 + self.low * (1 - 0.178404), 12), ts_sum(self.volume.rolling(120).mean(), 3), 16))) < (-1 * standard_rank(delta((self.high + self.low) / 2 * 0.178404 + self.vwap * (1 - 0.178404), 3)))
        alpha_064[judgement] = 1
        return alpha_064
      
    def alpha_065(self):
        alpha_065 = pd.DataFrame(-np.ones_like(self.close), index=self.close.index, columns=self.close.columns)
        judgement = standard_rank(correlation(open * 0.00817205 + vwap * (1 - 0.00817205), ts_sum(volume.rolling(60).mean(), 8), 6)) < standard_rank(-1 * (open - ts_min(open, 13)))
        alpha_065[judgement] = 1
        return alpha_065
    
    def alpha_066(self):
        return -1 * (standard_rank(decay_linear(delta(vwap, 3), 7)) + ts_rank(decay_linear((low - vwap) / (open - (high + low) / 2), 11), 6))
    
    def alpha_067(self):
        pass
    
    def alpha_068(self):
        alpha_068 = pd.DataFrame(-np.ones_like(self.close), index=self.close.index, columns=self.close.columns)
        judgement = (ts_rank(correlation(standard_rank(high), standard_rank(volume.rolling(15).mean()), 8), 13)) < (-1 * standard_rank(delta(close * 0.518371 + low * (1 - 0.518371), 1)))
        alpha_068[judgement] = 1
        return alpha_068
    
    def alpha_069(self):
        pass
    
    def alpha_070(self):
        pass
    
    def alpha_071(self):
        alpha_071 = pd.DataFrame(index=close.index, columns=close.columns)
        alpha_1 = ts_rank(decay_linear(correlation(ts_rank(close, 3), ts_rank(volume.rolling(180).mean(), 12), 18), 4), 15)
        alpha_2 = ts_rank(decay_linear(pow(standard_rank(low + open - 2 * vwap), 2), 16), 4)
        alpha_071[alpha_1 > alpha_2] = alpha_1
        alpha_071[alpha_1 <= alpha_2] = alpha_2
        return alpha_071
    
    def alpha_072(self):
        return standard_rank(decay_linear(correlation((high + low) / 2, volume.rolling(40).mean(), 8), 10)) / standard_rank(decay_linear(correlation(ts_rank(vwap, 3), ts_rank(volume, 18), 6), 2))
    
    def alpha_073(self):
        alpha_073 = pd.DataFrame(index=close.index, columns=close.columns)
        alpha_1 = standard_rank(decay_linear(delta(vwap, 4), 2))
        alpha_2 = -1 * ts_rank(decay_linear(-1 * delta(open * 0.147155 + low * (1 - 0.147155), 2) / (open * 0.147155 + low * (1 - 0.147155)), 3), 16)
        alpha_073[alpha_1 > alpha_2] = alpha_1
        alpha_073[alpha_1 <= alpha_2] = alpha_2
        return alpha_073
    
    def alpha_074(self):
        alpha_074 = pd.DataFrame(-np.ones_like(close), index=close.index, columns=close.columns)
        judgement = (standard_rank(correlation(close, ts_sum(volume.rolling(30).mean(), 37), 15))) < (-1 * standard_rank(correlation(standard_rank(high * 0.0261661 + vwap * (1 - 0.261661)), standard_rank(volume), 11)))
        alpha_074[judgement] = 1
        return alpha_074
    
    def alpha_075(self):
        alpha_075 = pd.DataFrame(-np.ones_like(close), index=close.index, columns=close.columns)
        judgement = standard_rank(correlation(vwap, volume, 4)) < standard_rank(correlation(standard_rank(low), standard_rank(volume.rolling(50).mean()), 12))
        alpha_075[judgement] = 1
        return alpha_075
    
    def alpha_076(self):
        pass
    
    def alpha_077(self):
        alpha_077 = pd.DataFrame(index=close.index, columns=close.columns)
        alpha_1 = standard_rank(decay_linear((high + low) / 2 - vwap, 20))
        alpha_2 = standard_rank(decay_linear(correlation((high + low) / 2, volume.rolling(40).mean(), 3), 5))
        alpha_077[alpha_1 > alpha_2] = alpha_1
        alpha_077[alpha_1 <= alpha_2] = alpha_2
        return alpha_077
    
    def alpha_078(self):
        return pow(standard_rank(correlation(ts_sum(low * 0.352233 + vwap * (1 - 0.352233), 19), ts_sum(volume.rolling(40).mean(), 19), 6)), standard_rank(correlation(standard_rank(vwap), standard_rank(volume), 5)))
    
    def alpha_079(self):
        pass
    
    def alpha_080(self):
        pass
    
    def alpha_081(self):
        #???
        pass
    
    def alpha_082(self):
        pass
    
    def alpha_083(self):
        return standard_rank(delay((high - low) / ts_sum(close, 5) / 5, 2)) * standard_rank(standard_rank(volume)) / ((high - low) / (ts_sum(close, 5)) / 5 / (vwap - close)) 
    
    def alpha_084(self):
        return ts_rank(vwap - ts_max(vwap, 15), 20) ** (delta(close, 4))
    
    def alpha_085(self):
        return standard_rank(correlation(high * 0.876703 + close * (1 - 0.876703), ad(volume, 30), 9)) ** standard_rank(correlation(ts_rank((high + low) / 2, 3), ts_rank(volume, 10), 7))
    
    def alpha_086(self):
        alpha_086 = pd.DataFrame(-np.ones_like(close), index=close.index, columns=close.columns)
        judgement = (ts_rank(correlation(close, ts_sum(ad(volume, 20), 14), 6), 20)) < standard_rank(-1 * (close - vwap))
        alpha_086[judgement] = 1
        return alpha_086
        
    def alpha_087(self):
        pass
    
    def alpha_088(self):
        alpha_088 = pd.DataFrame(index=close.index, columns=close.columns)
        alpha_1 = standard_rank(decay_linear(standard_rank(open) + standard_rank(low) + standard_rank(high) + standard_rank(close), 8))
        alpha_2 = ts_rank(decay_linear(correlation(ts_rank(close, 8), ts_rank(ad(volume, 60), 20), 8), 6), 2)
        alpha_088[alpha_1 < alpha_2] = alpha_1
        alpha_088[alpha_1 >= alpha_2] = alpha_2
        return alpha_088
    
    def alpha_089(self):
        pass
    
    def alpha_090(self):
        pass
    
    def alpha_091(self):
        pass
    
    def alpha_092(self):
        alpha_temp = pd.DataFrame(-np.ones_like(close), index=close.index, columns=close.columns)
        judgement_temp = ((high + low) / 2 + close) < (low + open)
        alpha_temp[judgement_temp] = 1
        alpha_1 = ts_rank(decay_linear(alpha_temp, 14), 18)
        alpha_2 = ts_rank(decay_linear(correlation(standard_rank(low), standard_rank(ad(volume, 30)), 7), 6), 6)
        alpha_092 = pd.DataFrame(index=close.index, columns=close.columns)
        alpha_092[alpha_1 < alpha_2] = alpha_1
        alpha_092[alpha_1 >= alpha_2] = alpha_2
        return alpha_092
        
    def alpha_093(self):
        pass
    
    def alpha_094(self):
        return -1 * standard_rank(vwap - ts_min(vwap, 11)) ** ts_rank(correlation(ts_rank(vwap, 19), ts_rank(ad(volume, 60), 4), 18), 2)
    
    def alpha_095(self):
        alpha_095 = pd.DataFrame(-np.ones_like(close), index=close.index, columns=close.columns)
        alpha_1 = standard_rank(open - ts_min(open, 12))
        alpha_2 = ts_rank(standard_rank(correlation(ts_sum((high + low) / 2, 19), ts_sum(ad(volume, 40), 19), 12)), 11)
        alpha_095[alpha_1 < alpha_2] = 1
        return alpha_095
        
    def alpha_096(self):
        alpha_096 = pd.DataFrame(index=close.index, columns=close.columns)
        alpha_1 = ts_rank(decay_linear(correlation(standard_rank(vwap), standard_rank(volume), 3), 4), 8)
        alpha_2 = ts_rank(decay_linear(ts_argmax(correlation(ts_rank(close, 7), ts_rank(ad(volume, 60), 4), 3), 12), 14), 13)
        alpha_096[alpha_1 > alpha_2] = -alpha_1
        alpha_096[alpha_1 <= alpha_2] = -alpha_2
        return alpha_096
        
    def alpha_097(self):
        pass
    
    def alpha_098(self):
        return standard_rank(decay_linear(correlation(vwap, ts_sum(ad(volume, 5), 26), 4), 7)) - standard_rank(decay_linear(ts_rank(ts_argmin(correlation(standard_rank(open), standard_rank(ad(volume, 15)), 20), 8), 6), 8))
    
    def alpha_099(self):
        alpha_099 = pd.DataFrame(-np.ones_like(close), index=close.index, columns=close.columns)
        alpha_1 = standard_rank(correlation(ts_sum((high + low) / 2, 19), ts_sum(ad(volume, 60), 19), 8))
        alpha_2 = standard_rank(correlation(low, volume, 6))
        alpha_099[alpha_1 >= alpha_2] = 1
        return alpha_099
    
    def alpha_100(self):
        pass
        
    def alpha_101(self):
        return (self.close - self.open) / (self.high - self.low) + 0.001
