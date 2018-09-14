# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 16:06:53 2018

@author: Pikari
"""

import numpy as np

def tanh(unit):
    return np.tanh(unit)

def sigmoid(unit):
    return 1 / (1 + np.exp(-unit))

def tanh_derivative(unit):
    return 1 - np.power(tanh(unit), 2)

def sigmoid_derivative(unit):
    return sigmoid(unit) * (1 - sigmoid(unit))

class BackPropagation():
    
    def __init__(self, layers, actfunc='sigmoid'):
        
        # 隐含层层数
        self.layers = layers
        
        # 初始化权重
        self.weight = self._init_random_weight()
        
        # 初始化阈值
        self.bias = self._init_random_bias()
        
        # 激活函数
        if actfunc == 'sigmoid':
            self.activation = sigmoid
            self.derivative = sigmoid_derivative
        
        elif actfunc == 'tanh':
            self.activation = tanh
            self.derivative = tanh_derivative
    
    # 随机产生权重    
    def _init_random_weight(self):
        weight = [2 * np.random.random((n1, n2)) - 1 for n1, n2 in zip(self.layers[:-1], self.layers[1:])]
        return weight
    
    # 随机产生阈值
    def _init_random_bias(self):
        bias = [2 * np.random.random((n)) - 1 for n in self.layers[1:]]
        return bias
    
    # 数据训练
    def train(self, x, y, learning_rate=0.1, max_iterations=2000):
        
        for i in range(max_iterations):
            
            # 随机选取一个样本
            r = np.random.randint(x.shape[0])
            layers_input = [x[r]]
            true_value = y[r]
            
            #正向传递
            for j in range(len(self.layers)-1):
                layers_input.append(self.activation(self.weight[j].T.dot(layers_input[-1]) + self.bias[j]))
            
            #反向修正
            #误差计算
            #输出层：输出值的偏导数*（实际值-输出值）
            #隐藏层：输出值的偏导数*该层至下一层权重.dot下一层误差
            error = [self.derivative(layers_input[-1]) * (true_value - layers_input[-1])]
            
            for j in range(len(layers_input) - 2, 0, -1):
                error.append(self.derivative(layers_input[j]) * self.weight[j].dot(error[-1]))

            #修正权重，阈值
            #权重：原权重+学习率*上一层输出值.dot该层误差.T
            #阈值：原偏向+学习率*该层误差
            error.reverse()
            
            for j in range(len(self.layers)-1):
                self.weight[j] += learning_rate * layers_input[j].reshape((layers_input[j].shape[0], 1)).dot(error[j].reshape((1, error[j].shape[0])))
                self.bias[j] += learning_rate * error[j]
    
    # 数据预测
    def predict(self, x):
        output = np.array(x)
        
        for j in range(len(self.layers)-1):
            output = self.activation(output.dot(self.weight[j]) + self.bias[j])
        
        return output.reshape(-1)
    
if __name__ == '__main__':
    
    x = np.random.random((100, 5))
    y = np.random.randint(0, 3, 100)
    bp = BackPropagation(layers=[5,4,1])
    bp.train(x, y)
    bp.predict(x)
            