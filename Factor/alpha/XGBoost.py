# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 19:15:35 2018

@author: Pikari
"""

import numpy as np
from CART import DecisionTree

class xgboost(DecisionTree):
    
    def __init__(self, type, n_estimators, max_deep=None):
        
        # 继承decisiontree的属性
        super(xgboost, self).__init__(type, max_deep)
        
        # 数的棵数
        self.n_estimators = n_estimators
    
    # xgboost专用回归
    # 父类回归函数不兼容且在子类中会被调用
    def xg_fit(self, x, y):
        
        n = self.n_estimators # 数的剩余棵数
        self.xg_deep = [] # 储存所有树的深度
        self.xg_node = [] # 储存所有树的节点
        self.xg_clusters = [] # 储存所有树的叶片类别
        
        # 为零时停止生成
        while n:
            
            # 生成一颗cart回归树
            self.fit(x, y)
            self.xg_deep.append(self.deep)
            self.xg_node.append(self.node)
            self.xg_clusters.append(self.clusters)
            
            # 用当前回归树进行预测
            y_new = self.predict(x)
            
            # 获取残差进入下一棵树回归
            y = y - y_new
            n -= 1
    
    # xgboost专用预测
    def xg_predict(self, x):
        
        # 预测值
        pred = np.zeros_like(x[:, -1])
        
        for n in range(self.n_estimators):
            self.deep = self.xg_deep[n]
            self.node = self.xg_node[n]
            self.clusters = self.xg_clusters[n]
            
            pred = pred + self.predict(x)
            
        return pred
        
if __name__ == '__main__':
    
    from sklearn.datasets import load_iris
    iris = load_iris()
    x = iris.data
    y = iris.target

    xg = xgboost(type='regressor', n_estimators=5, max_deep=3)
    xg.xg_fit(x, y)
    result = xg.xg_predict(x)
    