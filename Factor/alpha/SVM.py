# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 13:15:28 2018

@author: Pikari
"""

import numpy as np

class SupportVectorMechine():
    
    def __init__(self, c=1, kernel=None, epsilon=1e-3):
        self.c = c # 松弛变量，默认为1
        self.kernel = kernel # 核函数
        self.epsilon = 1e-3
        
    # 初始化所有拉格朗日系数为0
    def _init_alpha(self):
        alpha = np.zeros_like(self.x[:, 0])
        return alpha
    
    # 计算预测值
    def calc_predict_value(self, x_i):
        pred = np.sum(x_i.dot(self.x.T) * self.alpha * self.y) + self.b
        return np.sign(pred)
    
    # 计算误差
    def calc_error(self, x_i, y_i):
        error = self.calc_predict_value(x_i) - y_i
        return error
    
    # 计算核內积
    def calc_kernel(self, x_i, x_j):
        kernel = x_i.dot(x_j)
        return kernel
    
    # 外部循环
    # 选取边界上违反KKT条件的样本点的索引
    def outer_loop(self):
        alpha_opt = []
        
        for i in range(len(self.x)):
            p = self.y[i] * self.calc_predict_value(self.x[i])
            a = self.alpha[i]
            
            if not (p == 1 and a > 0 and a < self.c) \
                or (p <= 1 and a == self.c) \
                or (p >= 1 and a == 0):
                alpha_opt.append(i)
                
        return alpha_opt
    
    # 内部循环
    # 选取误差最大
    # 返回索引及误差
    def inner_loop(self, i, alpha_opt):
        j = i    
        err = 0
        err_1 = self.calc_error(self.x[i], self.y[i])
        
        for k in alpha_opt:
            
            if i != k:
                error = err_1 - self.calc_error(self.x[k], self.y[k])
                
                if abs(error) > abs(err):
                    err = error
                    j = k
        
        return j, err
    
    # 计算eta
    def calc_eta(self, x_i, x_j):
        eta = x_i.dot(x_i) - 2 * x_i.dot(x_j) + x_j.dot(x_j)
        return eta
    
    def fit(self, x, y):
        self.x = x
        self.y = y
        
        self.alpha = self._init_alpha()
        self.b = 0
        
        # 满足一个终止条件即退出，未实现
        # 满足KKT条件
        # alpha不再变化
        while True:
            
            # 外部循环
            alpha_opt = self.outer_loop()
            
            # alpha更新法则
            # 详见SMO算法证明
            for i in alpha_opt:
                j, err = self.inner_loop(i, alpha_opt)
                x_i, x_j = self.x[i], self.x[j]
                y_i, y_j = self.y[i], self.y[j]
                err_i, err_j = self.calc_error(x_i, y_i), self.calc_error(x_j, y_j)
                alpha_i_old, alpha_j_old = self.alpha[i], self.alpha[j]
                
                if y_i == y_j:
                    l = max(0, alpha_i_old + alpha_j_old - self.c)
                    h = min(self.c, alpha_i_old + alpha_j_old)
                    
                else:
                    l = max(0, alpha_j_old - alpha_i_old)
                    h = min(self.c, self.c + alpha_j_old - alpha_i_old)
                    
                eta = self.calc_eta(x_i, x_j)
                alpha_j_new = alpha_j_old + y_j * err / eta
                
                if alpha_j_new > h:
                    alpha_j_new = h
                    
                elif alpha_j_new < l:
                    alpha_j_new = l
                    
                alpha_i_new = alpha_i_old - y_i * y_j * (alpha_j_new - alpha_j_old)
                self.alpha[i], self.alpha[j] = alpha_i_new, alpha_j_new
                
                b_i = self.b - err_i - y_i * \
                      (alpha_i_new - alpha_i_old) * x_i.dot(x_i) - \
                      y_j * (alpha_j_new - alpha_j_old) * x_i.dot(x_j)
                b_j = self.b - err_j - y_i * \
                      (alpha_i_new - alpha_i_old) * x_i.dot(x_j) - \
                      y_j * (alpha_j_new - alpha_j_old) * x_j.dot(x_j)
                      
                if alpha_i_new > 0 and alpha_i_new < self.c:
                    self.b = b_i
                    
                elif alpha_j_new > 0 and alpha_j_new < self.c:
                    self.b = b_j
                    
                else:
                    self.b = (b_i + b_j) / 2
                
            self.w = self.x.T.dot(svm.alpha * y)
            
            if np.sum(np.sign(self.x.dot(self.w) + self.b) - self.y) <= self.epsilon:
                break
    
    def predict(self, x):
        pred = np.sign(x.dot(self.w) + self.b)
        return pred
    
# 问题
# alpha仅循环一次之后便不再变化
# alpha不再变化后几乎所有样本均不满足KKT条件
# 可以准确分类，但不是最优超平面

if __name__ == '__main__':
    
    from sklearn.datasets import load_iris
    iris = load_iris()
    x = iris.data[50:150]
    y = iris.target[50:150]
    y[:50] = -1
    y[50:100] = 1

    svm = SupportVectorMechine()
    svm.fit(x, y)
    
#    from sklearn.svm import SVC
#    clf = SVC()
#    clf.fit(x, y)
#    pre = clf.predict(x)
