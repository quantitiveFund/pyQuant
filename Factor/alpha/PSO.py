# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 12:57:52 2018

@author: Pikari
"""

import random
import numpy as np
import pandas as pd

# 欧氏距离
def euclidean_distance(one_sample, data_sets):
    one_sample = one_sample.reshape(1, -1)
    data_sets = data_sets.reshape(data_sets.shape[0], -1)
    distances = np.power(np.tile(one_sample, (data_sets.shape[0], 1)) - data_sets, 2).sum(axis=1)
    return distances

class PSO():
    
    def __init__(self, data_sets, k=4, m=5, w=0.5, c1=2, c2=2, max_iterations=100):
        self.data_sets = data_sets # 训练集
        self.k = k # 粒子内样本数
        self.m = m # 粒子数
        self.w = w # 速度加权系数
        self.c1 = c1 # 学习因子
        self.c2 = c2 # 学习因子
        self.max_iterations = max_iterations # 最大迭代次数
        
        # 训练集样本数，维数        
        self.length, self.dimension = self.data_sets.shape
        
        # 最大坐标，最小坐标
        # 各个维度数值差异较大的须标准化
        self.max_location = np.nanmax(data_sets)
        self.min_location = np.nanmin(data_sets)
        
        # 最大速度
        self.max_velocity = self.max_location - self.min_location
        
        # 初始化位置，速度，局部最优点，全局最优点
        self.locations, self.velocity, self.p_best, self.g_best= self._init_random()
        
        # 计算初始位置的个体适应度值，全局适应度值
        self.p_fitness, self.g_fitness = self._init_fitness()
        
        # 历史适应度值
        self.fitness = []
        
    # 初始化位置，速度，局部最优点，全局最优点
    def _init_random(self):
        shape = (self.k, self.dimension)
        particles = [random.sample(range(self.length), self.k) for i in range(self.m)]
        locations = [self.data_sets[particle] for particle in particles]
        velocity = [(np.random.random(shape) - 0.5) * 2 * self.max_velocity for i in range(self.m)]
        p_best = [np.random.random(shape) * self.max_velocity + self.min_location for i in range(self.m)]
        g_best = np.random.random(shape) * self.max_velocity + self.min_location
        return locations, velocity, p_best, g_best
    
    # 聚类
    def create_clusters(self, particle, data_sets):
        clusters = [[] for i in range(self.k)]

        for sample_i, sample in enumerate(data_sets):
            distances = euclidean_distance(sample, particle)
            close_i = np.nanargmin(distances)
            clusters[close_i].append(sample_i)
        
        return clusters
    
    # 计算适应度值
    def calculate_fitness(self, particle, data_sets, clusters):
        fitness = sum([((data_sets[cluster] - center) ** 2).sum() for (cluster, center) in zip(clusters, particle)])
        return fitness
    
    # 更新速度
    def update_velocity(self):
        r1, r2 = random.random(), random.random()
        velocity = [self.w * v + self.c1 * r1 * (p - l) + self.c2 * r2 * (self.g_best - l) for (v, p, l) in zip(self.velocity, self.p_best, self.locations)]
        return velocity
    
    # 更新位置
    def update_locations(self):
        locations = [l + v for (l, v) in zip(self.locations, self.velocity)]
        return locations
    
    # 计算初始位置的个体适应度值，全局适应度值
    def _init_fitness(self):
        p_fitness = []
        
        for p_particle in self.p_best:
            p_clusters = self.create_clusters(p_particle, self.data_sets)
            p_fitness.append(self.calculate_fitness(p_particle, self.data_sets, p_clusters))
        
        g_cluster = self.create_clusters(self.g_best, self.data_sets)
        g_fitness = self.calculate_fitness(self.g_best, self.data_sets, g_cluster)
        return p_fitness, g_fitness
    
    # 数据训练
    def predict(self):
        
        for i in range(self.max_iterations):
            self.velocity = self.update_velocity()
            self.locations = self.update_locations()
            self.fitness = []
            
            for particle in self.locations:
                clusters = self.create_clusters(particle, self.data_sets)
                
                self.fitness.append(self.calculate_fitness(particle, self.data_sets, clusters))
            
            self.p_best = [new_location if new_fitness < old_fitness else old_location for (new_location, new_fitness, old_fitness, old_location) in zip(self.locations, self.fitness, self.p_fitness, self.p_best)]
            self.p_fitness = [new_fitness if new_fitness < old_fitness else old_fitness for (new_fitness, old_fitness) in zip(self.fitness, self.p_fitness)]
            
            # 若更新位置后适应度值小于全局最优适应度值，则保留该位置及其适应度值
            for p_b, p_f in zip(self.p_best, self.p_fitness):
                
                if p_f < self.g_fitness:
                    self.g_best = p_b
                    self.g_fitness = p_f

if __name__ == '__main__':
    
    data = pd.read_table('movement.txt', sep=',')
    
    for row in data.columns:
        data[row] = (data[row] - data[row].min()) / (data[row].max() - data[row].min())
        
    #data = pd.read_csv('pso.csv', index_col=0).dropna().T
    particle_data = np.array(data.values)
    pso = PSO(particle_data, k=15)
    pso.predict()
    centriods = pso.g_best
    