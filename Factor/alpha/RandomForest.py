# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 16:29:06 2018

@author: Pikari
"""

import numpy as np
from CART import DecisionTree

class RandomForest(DecisionTree):
    
    def __init__(self, type, n_estimators=10, max_deep=None):
        super(RandomForest, self).__init__(type, max_deep)
        self.n_estimators = n_estimators
    
    # 随机选取若干特征值
    def _init_feature_values(self, x):
        random_features = []
        
        for i in range(self.max_features):
            random_features.append([])
            
            for j in range(int(np.floor(10))):
                random_features[i].append(np.random.choice(x[:, i]))
        
        return random_features
    
    def rf_fit(self, x, y):
        n = self.n_estimators
        
        self.rf_deep = []
        self.rf_node = []
        self.rf_clusters = []
        
        while n:
            self.fit(x, y)
            self.rf_deep.append(self.deep)
            self.rf_node.append(self.node)
            self.rf_clusters.append(self.clusters)
            
            n -= 1
    
    def rf_predict(self, x):
        pred = np.zeros_like(x[:, -1])
        
        for n in range(self.n_estimators):
            self.deep = self.rf_deep[n]
            self.node = self.rf_node[n]
            self.clusters = self.rf_clusters[n]
            
            pred = pred + self.predict(x)
            
        # 返回一个简单平均
        return np.round(pred / self.n_estimators)

if __name__ == '__main__':
    
    from sklearn.datasets import load_iris
    iris = load_iris()
    x = iris.data
    y = iris.target

    rf = RandomForest(type='classifier', n_estimators=10, max_deep=3)
    rf.rf_fit(x, y)
    result = rf.rf_predict(x)    
    