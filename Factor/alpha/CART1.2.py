# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 14:31:29 2018

@author: Pikari
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class DecisionTree():
    
    def __init__(self):
        pass
    
    # 获取每个特征的值
    def _init_feature_values(self, x):
        feature_values = [np.unique(x[:, i]).tolist() for i in range(self.max_features)]
        return feature_values
    
    # 计算初始基尼系数
    # y为类别数据
    def _init_gini(self, y):
        p = np.array([np.sum(y==res) / len(y) for res in np.unique(y)])
        gini = 1 - np.sum(np.power(p, 2))
        return gini
    
    # 计算某一节点分类后的基尼系数
    def calculate_gini(self, classify):
        gini = 0
        
        for cla in classify:
            cla_y = cla[:, -1]
            p = np.array([np.sum(cla_y==res) / len(cla) for res in np.unique(cla_y)])
            weight = len(cla) / len(self.y)
            gini += (1 - np.sum(np.power(p, 2))) * weight
        
        return gini
    
    # 依据基尼系数获取最优节点
    def create_node(self, cla):
        
        # 若该节点样本为同一类或无样本，返回空列表
        if cla.tolist() == [] or np.unique(cla[:, -1]).shape[0] == 1:
            return []
        
        # 反之返回最优节点[特征项， 特征值]
        else:
            leaf = []
            leaf_gini = []
            
            for features_i, features in enumerate(self.feature_values):
                gini = self._init_gini(cla[:, -1])
                
                for feature in features:
                    leaf_cla = [cla[cla[:, features_i] <= feature], 
                                cla[cla[:, features_i] > feature]]
                    gini_new = self.calculate_gini(leaf_cla)
                    
                    if gini_new < gini:
                        gini = gini_new
                        leaf.append([features_i, feature])
                        leaf_gini.append(gini)
                        
            return leaf[np.argmin(leaf_gini)]
    
    # 依据节点，特征生成下一层节点
    def create_leaf(self, cla, node):
        
        if node == [] or cla.tolist() == [] or np.unique(cla[:, -1]).shape[0] == 1:
            return [np.array([]), np.array([])]
        else:
            feature_i = node[0]
            feature = node[1]
            leaf = [cla[cla[:, feature_i] <= feature], 
                    cla[cla[:, feature_i] > feature]]
            return leaf
    
    # 训练
    def fit(self, x, y, max_deep=3):
        
        self.x = x
        self.y = y
        self.max_deep = max_deep
        
        # 训练集个数，训练集维数
        self.samples, self.max_features = x.shape
        
        # 获取训练集特征值
        self.feature_values = self._init_feature_values(x)
        
        data_sets = np.c_[x, y]
        
        # 训练集，key为层数，value为[np.array()] * (2 ** (key))
        # key <= max_deep - 1
        # np.array([])为剪枝
        classify = {key : [] for key in range(self.max_deep)}
        classify[0].append(data_sets)
        
        # 节点，key为层数，value为[[特征项，特征值]] * (2 ** (key))
        # key <= max_deep - 2
        # []为剪枝
        self.node = {key : [] for key in range(self.max_deep-1)}
        
        # 若该节点样本为同一类或者不存在样本，则做剪枝处理
        for i in range(self.max_deep-1):
            
            for cla in classify[i]:
                
                node = self.create_node(cla)
                leaf = self.create_leaf(cla, node)
                self.node[i] += [node]
                classify[i+1] += leaf
        
        self.clusters = self.create_clusters(classify)
        
        return classify
    
    # 各层节点分类情况
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
                    for res in np.unique(self.y):
                        p[clu_i].append(np.sum(clu[:, -1]==res))
                    p[clu_i] = np.argmax(p[clu_i])
        
            clusters[key] = p
        
        return clusters        
    
    # 预测
    # np.array([])为剪枝
    def predict(self, x):
        pre = np.c_[np.array(x), -np.ones(x[:, -1].shape)]
        classify = {key : [] for key in range(self.max_deep)}
        classify[0].append(x)
        
        # 生成树体
        for i in range(self.max_deep-1):
            
            for cla, node, clu in zip(classify[i], self.node[i], self.clusters[i]):
                
                leaf = self.create_leaf(cla, node)
                classify[i+1] += leaf
        
        # 生成分类标签
        for i in range(self.max_deep):
            
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

    dt = DecisionTree()
    classify = dt.fit(x, y, max_deep=4)
    prediction = dt.predict(x)
        
    print(np.sum(prediction[:, -1] == y) / len(y))
    