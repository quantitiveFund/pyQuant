# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 14:35:32 2018

@author: Pikari
"""

import numpy as np
import matplotlib.pyplot as plt

class DecisionTree():
    
    def __init__(self):
        pass
    
    # 获取每个特征的值
    def _init_feature_values(self, x):
        feature_values = [np.unique(x[:, i]).tolist() for i in range(self.max_features)]
        return feature_values
    
    # 随机生成一个树体
    def random_tree_node(self):
        tree_node = [[np.random.choice(v), f] for f, v in enumerate(self.feature_values)]
        np.random.shuffle(tree_node)
        return tree_node
    
    # 计算初始熵值
    def _init_entropy(self, y):
        entropy = 0
        for res in np.unique(y):
            p = y[y==res].shape[0] / y.shape[0]
            entropy -= p * np.log(p)
        return entropy
    
    # 数据训练
    def fit(self, x, y, max_iterations=200):
        
        # 训练集个数，训练集维数
        self.samples, self.max_features = x.shape
        
        # 获取训练集特征值
        self.feature_values = self._init_feature_values(x)
        
        # 计算训练集熵值
        self.entropy = self._init_entropy(y)
        
        # 整合训练集与实际类别数据
        data_sets = np.c_[x, y]
        
        # 迭代
        for i in range(max_iterations):
            
            # 随机生成树体
            tree_node = self.random_tree_node()
            
            # 生成叶片
            leaf = {}
            for node_i, node in enumerate(tree_node):
                
                if node_i == 0:
                    leaf[node_i] = [data_sets[data_sets[:, node[1]] <= node[0]], 
                                    data_sets[data_sets[:, node[1]] > node[0]]]
            
                else:
                    leaf_last = leaf[node_i-1]
                    leaf[node_i] = []
                    
                    for l in leaf_last:
                        leaf[node_i].append(l[l[:, node[1]] <= node[0]])
                        leaf[node_i].append(l[l[:, node[1]] > node[0]])
            
            # 获取分类结果
            results = leaf[node_i]
            
            # 计算权重，概率
            w = np.array([root.shape[0] / x.shape[0] for root in results])
            p = [[] for i in range(len(results))]
            
            for root_i, root in enumerate(results):
                
                for res in np.unique(y):
                    
                    if root.shape[0] == 0:
                        p[root_i].append(0)
                    else:
                        p[root_i].append(root[root[:, -1] == res].shape[0] / root.shape[0])
            
            # 依据权重，概率计算熵值
            p = np.array(p)
            entropy = (np.nansum(-p * np.log(p), axis=1) * w).sum()
            
            # 熵值减小，则保留该树体及叶片分类情况
            if entropy < self.entropy:
                self.entropy = entropy
                self.tree_node = tree_node
                
                # 叶片分类情况，若同意叶片下有多类，则该叶片记为数量最多的那一类 
                self.classify = np.argmax(p, axis=1)
    
    # 数据预测
    def predict(self, x):
        
        # 生成叶片
        leaf = {}
        for node_i, node in enumerate(self.tree_node):
            
            if node_i == 0:
                leaf[node_i] = [x[x[:, node[1]] <= node[0]], x[x[:, node[1]] > node[0]]]
        
            else:
                leaf_last = leaf[node_i-1]
                leaf[node_i] = []
                
                for l in leaf_last:
                    leaf[node_i].append(l[l[:, node[1]] <= node[0]])
                    leaf[node_i].append(l[l[:, node[1]] > node[0]])
        
        # 分类结果
        results = leaf[node_i]
        
        # 分类汇总
        clusters = []
        
        for c_i, c in enumerate(self.classify):
            cla = results[c_i].tolist()
            
            if cla != []:
                
                # 添加具体分为哪一类的数据
                for each in cla:
                    each.append(c)
                    clusters.append(each)
        
        return np.array(clusters)

if __name__ == '__main__':
    
    # 随机产生树体
    # 未剪枝
    # 分类结果顺序被打乱
    
    from sklearn.datasets import load_iris
    iris = load_iris()
    x = iris.data
    y = iris.target
    
    dt = DecisionTree()
    dt.fit(x, y, max_iterations=100)
    
    classify = dt.predict(x)
    results = classify[:, -1]

    plt.scatter(classify[results==0][:, 0], classify[results==0][:, 1])
    plt.scatter(classify[results==1][:, 0], classify[results==1][:, 1])
    plt.scatter(classify[results==2][:, 0], classify[results==2][:, 1])

#    from sklearn.datasets import load_iris
#    from sklearn.tree import DecisionTreeClassifier
#    clf = DecisionTreeClassifier(random_state=0)
#    iris = load_iris()
#    clf.fit(iris.data, iris.target)
#    results = clf.predict(iris.data)
#    plt.scatter(x[results==0][:, 0], x[results==0][:, 1])
#    plt.scatter(x[results==1][:, 0], x[results==1][:, 1])
#    plt.scatter(x[results==2][:, 0], x[results==2][:, 1])
