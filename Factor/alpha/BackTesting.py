# -*- coding: utf-8 -*-
"""
Created on Thu May 17 19:13:12 2018

@author: Pikari
"""

from abc import ABCMeta, abstractmethod
import pandas as pd
from queue import Queue
import datetime
import mysql.connector

conn = mysql.connector.connect(host='10.23.0.2', user='root', password='******', database='quant')
cursor = conn.cursor()

class Event(object):
    pass

class MarketEvent(Event):
    def __init__(self):
        self.type = 'MARKET'

class SignalEvent(Event):
    def __init__(self, symbol, datetime, signal_type):
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        
class OrderEvent(Event):
    def __init__(self, symbol, order_type, quantity, direction):
        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction
    
    def to_dict(self):
        dictionary = {'symbol' : self.symbol, 
                      'order_type' : self.order_type, 
                      'quantity' : self.quantity, 
                      'direction' : self.direction}
        return dictionary
        
class FillEvent(Event):
    def __init__(self, timeindex, symbol, cost, quantity, direction, commission=0):
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.cost = cost
        self.quantity = quantity
        self.direction = direction
        if commission == 0:
            self.commission = self.calculate_commission()
        else:
            self.commission = commission
     
    def calculate_commission(self):
        pass
    
class DataHandler(object):
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_latest_data(self, symbol, n=1):
        raise NotImplemented
        
    @abstractmethod
    def update_data(self):
        raise NotImplemented

class DatabaseHandler(DataHandler):
    def __init__(self, events, symbol_list):
        self.events = events
        self.symbol_list = symbol_list
        
        self.symbol_data = {}
        self.symbol_lastest_data = {}
        self.contiune = True
        self.generator = {}
        
        self._load_from_database()
        self._get_generator()
        
    def _load_from_database(self):
        for symbol in self.symbol_list:
            self.symbol_data[symbol] = pd.read_sql('select * from %s' % symbol, conn, index_col='Date')
            
            self.symbol_lastest_data[symbol] = [] 
            
    def _get_new_bars(self, symbol):
        for index, row in self.symbol_data[symbol].iterrows():
            yield tuple([symbol, index, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]])
    
    def _get_generator(self):
        for symbol in self.symbol_list:
            self.generator[symbol] = self._get_new_bars(symbol)
            
    def get_latest_data(self, symbol, n=1):
        try:
            bars_list = self.symbol_lastest_data[symbol]
        except KeyError:
            print('GG')
        else:
            return bars_list[-n:]
    
    def update_data(self):
        for symbol in self.symbol_list:
            try:
                bars = next(self.generator[symbol])
            except StopIteration:
                self.contiune = False
            else:
                if bars is not None:
                    self.symbol_lastest_data[symbol].append(bars)
        #???
        self.events = MarketEvent()
      
class Portfolio(object):
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def update_signal(self, event):
        raise NotImplemented
        
    @abstractmethod
    def update_fill(self, event):
        raise NotImplemented
      
class NaviePortfolio(Portfolio):
    def __init__(self, bars, events, start_date, initial_cash=1000000):
        self.bars = bars
        self.events = events
        self.start_date = start_date
        self.initial_cash = initial_cash
        self.symbol_list = self.bars.symbol_list
        
        self.all_positions = self.construct_all_positions()
        self.current_positions = dict((keys, values) for keys, values in [(symbol, 0) for symbol in self.symbol_list])
    
        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()
        
    def construct_all_positions(self):
        dictionary = dict((keys, values) for keys, values in [(symbol, 0) for symbol in self.symbol_list])
        dictionary['datetime'] = self.start_date
        return [dictionary]
        
    def construct_all_holdings(self):
        dictionary = dict((keys, values) for keys, values in [(symbol, 0) for symbol in self.symbol_list])
        dictionary['datetime'] = self.start_date
        dictionary['cash'] = self.initial_cash
        dictionary['commission'] = 0
        dictionary['total'] = self.initial_cash
        return [dictionary]
    
    def construct_current_holdings(self):
        dictionary = dict((keys, values) for keys, values in [(symbol, 0) for symbol in self.symbol_list])
        dictionary['cash'] = self.initial_cash
        dictionary['commission'] = 0
        dictionary['total'] = self.initial_cash
        return dictionary
    
    def update_timeindex(self, event):
        bars = {}
        for symbol in self.symbol_list:
            bars[symbol] = self.bars.get_latest_data(symbol)
        
        positions_dict = dict((keys, values) for keys, values in [(symbol, 0) for symbol in self.symbol_list])
        positions_dict['datetime'] = bars[self.symbol_list[0]][0][1]
        
        for symbol in self.symbol_list:
            positions_dict[symbol] = self.current_positions[symbol]
            
        self.all_positions.append(positions_dict)
        
        holdings_dict = dict((keys, values) for keys, values in [(symbol, 0) for symbol in self.symbol_list])
        holdings_dict['datetime'] = bars[self.symbol_list[0]][0][1]
        holdings_dict['cash'] = self.current_holdings['cash']
        holdings_dict['commission'] = self.current_holdings['commission']
        holdings_dict['total'] = self.current_holdings['cash']
        
        for symbol in self.symbol_list:
            market_value = self.current_holdings[symbol] * bars[symbol][0][5]
            holdings_dict[symbol] = market_value
            holdings_dict['total'] += market_value
            
        self.all_holdings.append(holdings_dict)

    def update_positions_from_fill(self, fill):
        fill_direction = 0
        if fill.direction == 'BUY':
            fill_direction = 1
        if fill.direction == 'SELL':
            fill_direction = -1
            
        self.current_positions[fill.symbol] += fill_direction * fill.quantity

    def update_holdings_from_fill(self, fill):
        fill_direction = 0
        if fill.direction == 'BUY':
            fill_direction = 1
        if fill.direction == 'SELL':
            fill_direction = -1
            
        fill_cost = self.bars.get_latest_data(fill.symbol)[0][5]
        cost = fill_direction * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= cost + fill.commission
        self.current_holdings['total'] -= cost + fill.commission
    
    def update_fill(self, event):
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)
            
class Strategy(object):
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError

class BuyHoldStrategy(Strategy):
    def __init__(self, bars, events):
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        
    def _calculate_initial_bought(self):
        bought = {}
        for symbol in self.symbol_list:
            bought[symbol] = False
        return bought
    
    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                bars = self.bars.get_latest_bars(symbol)
                if bars is not None and bars != []:
                    if self.bought[symbol] == False:
                        signal = SignalEvent(bars[0][0], bars[0][1], 'LONG')
                        self.events.put(signal)
                        self.bought[symbol] = True
                        
class ExecutionHandler(object):
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def execute_order(self, event):
        raise NotImplementedError
        
class SimulatedExecutionHandler(ExecutionHandler):
    def __init__(self, events):
        self.events = events
        
    def execute_order(self, event):
        if event.type == 'ORDER':
            fill_event = FillEvent(datetime.datetime.utcnow(), event.symbol, 'ARCA', event.quantity, event.direction, None)
            self.events.put(fill_event)
            
symbol_list = ['stock_000830', 'stock_603999']
data = DatabaseHandler(MarketEvent(), symbol_list)
data.update_data()
bars = data.symbol_lastest_data
order = OrderEvent(symbol_list[0], 'MARKET_PRICE', 100, 'BUY')
fill = FillEvent(datetime.datetime.utcnow(), symbol_list[0], bars[symbol_list[0]][0][2] * 100, 100, 'BUY', 5)
#strategy = BuyHoldStrategy(bars, )
port = NaviePortfolio(data, Event(), '2015-12-25')