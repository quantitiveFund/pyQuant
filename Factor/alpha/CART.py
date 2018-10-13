# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 14:31:29 2018

@author: Pikari
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class DecisionTree():
    
    def __init__(self, type):
        # 回归或分类
        # 'regressor' or 'classifier'
        self.type = type
    
    # 获取每个特征的值
    # x为训练集
    # 返回值为特征项的所有特征值
    def _init_feature_values(self, x):
        feature_values = [np.unique(x[:, i]).tolist() for i in range(self.max_features)]
        return feature_values
    
    # 计算初始gain
    # y为目标集
    def _init_gain(self, y):
        
        if self.type == 'classifier':
            p = np.array([np.sum(y==res) / len(y) for res in np.unique(y)])
            gini = 1 - np.sum(np.power(p, 2))
            return gini
        
        elif self.type == 'regressor':
            sigma = np.std(y)
            return sigma
    
    # 计算某一节点分类后的gain
    # leaf_cla为[np.array()]
    def calculate_gain(self, leaf_cla):
        
        if self.type == 'classifier':
            gini = 0
            
            for cla in leaf_cla:
                cla_y = cla[:, -1]
                p = np.array([np.sum(cla_y==res) / len(cla) for res in np.unique(cla_y)])
                weight = len(cla) / len(self.y)
                gini += (1 - np.sum(np.power(p, 2))) * weight
            
            return gini
        
        elif self.type == 'regressor':
            sigma = 0
            
            for cla in leaf_cla:
                
                # np.std(np.array([])) = np.nan
                # 出现上述情况会报错
                if cla.shape[0] != 0:
                    sigma += np.std(cla[:, -1])
            
            return sigma
                
    # 依据gain获取最优节点
    # cla为np.array()
    def create_node(self, cla):
        
        # 若该节点样本为同一类或无样本,返回空列表
        if cla.tolist() == [] or np.unique(cla[:, -1]).shape[0] == 1:
            return []
        
        # 反之返回最优节点[特征项, 特征值]
        else:
            leaf = []
            leaf_gain = []
            
            for features_i, features in enumerate(self.feature_values):
                gain = self._init_gain(cla[:, -1])
                
                for feature in features:
                    leaf_cla = [cla[cla[:, features_i] <= feature], 
                                cla[cla[:, features_i] > feature]]
                    gain_new = self.calculate_gain(leaf_cla)
                    
                    if gain_new < gain:
                        gain = gain_new
                        leaf.append([features_i, feature])
                        leaf_gain.append(gain)
            
            # 无最优二分类情况下,返回[]
            # 反之返回最优节点
            if leaf_gain == []:            
                return []
            else:
                return leaf[np.argmin(leaf_gain)]
    
    # 依据节点,特征生成下一层节点
    # cla为np.array()
    # node为[特征项,特征值]
    def create_leaf(self, cla, node):
        
        # 无最优分类、无样本、样本为同一类
        if node == [] or cla.tolist() == [] or np.unique(cla[:, -1]).shape[0] == 1:
            return [np.array([]), np.array([])]
        else:
            feature_i = node[0]
            feature = node[1]
            leaf = [cla[cla[:, feature_i] <= feature], 
                    cla[cla[:, feature_i] > feature]]
            return leaf
    
    # 训练
    def fit(self, x, y):
        
        self.x = x
        self.y = y
        
        # 训练集个数,训练集维数
        self.samples, self.max_features = x.shape
        
        # 获取训练集特征值
        self.feature_values = self._init_feature_values(x)
        
        data_sets = np.c_[x, y]
        
        # 训练集,key为层数,value为[np.array()] * (2 ** (key))
        # np.array([])为剪枝
        classify = {0 : [data_sets]}
        
        # 节点,key为层数,value为[[特征项,特征值]] * (2 ** (key))
        # []为剪枝
        self.node = {0 : []}
        
        # 若该节点样本为同一类或者不存在样本,则做剪枝处理
        i = 0
        
        while True:
            
            # count计数node为[]的情况
            # 若count=0,则node全为[],训练结束
            count = 0
            self.node[i] = []
            classify[i+1] = []
            
            for cla in classify[i]:
                node = self.create_node(cla)
                leaf = self.create_leaf(cla, node)
                self.node[i] += [node]
                classify[i+1] += leaf
                
                if node != []:
                    count += 1
            
            i += 1
            
            if count == 0:
                break
            
        self.clusters = self.create_clusters(classify)
        self.deep = len(classify)
        
        return classify
    
    # 各层节点分类情况
    # classify为{[np.array()]}
    # nan为剪枝
    def create_clusters(self, classify):
        clusters = {}
        
        for key in classify.keys():
            cluster = classify[key]
            p = [[] for i in range(len(cluster))]
            
            for clu_i, clu in enumerate(cluster):
            
                if clu.tolist() == []:
                    p[clu_i] = np.nan
                else:
                    
                    if self.type == 'classifier':
                        
                        for res in np.unique(self.y):
                            p[clu_i].append(np.sum(clu[:, -1]==res))
                            
                        p[clu_i] = np.argmax(p[clu_i])
                    
                    elif self.type == 'regressor':
                        p[clu_i] = np.mean(clu[:, -1])
            
            clusters[key] = p
        
        return clusters        
    
    # 预测
    # np.array([])为剪枝
    def predict(self, x):
        pre = np.c_[np.array(x), -np.ones(x[:, -1].shape)]
        classify = {key : [] for key in range(self.deep)}
        classify[0].append(x)
        
        # 生成树体
        for i in range(self.deep-1):
            
            for cla, node, clu in zip(classify[i], self.node[i], self.clusters[i]):
                
                leaf = self.create_leaf(cla, node)
                classify[i+1] += leaf
        
        # 生成分类标签
        for i in range(self.deep):
            
            for cla, clu in zip(classify[i], self.clusters[i]):
                
                for c in cla:
                    pre[np.argmax(np.sum(pre == c.tolist() + [-1], axis=1))][-1] = clu

        return pre
    
if __name__ == '__main__':
    
    from sklearn.datasets import load_iris
    iris = load_iris()
    x = iris.data
    y = iris.target
    
#    data = pd.read_table('seed.txt', sep=',')
#    x = data.values[:, :-1]
#    y = data.values[:, -1] - 1
    
    # 回归树
#    dt = DecisionTree('regressor')
#    classify = dt.fit(x, y)
#    prediction = dt.predict(x)
        
    # 分类树
    dt = DecisionTree('classifier')
    classify = dt.fit(x, y)
    prediction = dt.predict(x)
    print(np.sum(prediction[:, -1] == y) / len(y))
    
    # sklearn回归树
#    from sklearn import tree
#    clf = tree.DecisionTreeRegressor()
#    clf = clf.fit(x, y)
#    clf.predict(x)
  
    # sklearn分类树
#    from sklearn import tree
#    clf = tree.DecisionTreeClassifier()
#    clf = clf.fit(x, y)
#    clf.predict(x)
