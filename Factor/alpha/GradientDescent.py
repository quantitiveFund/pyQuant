# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 00:10:55 2018

@author: Pikari
"""

import numpy as np

def function(x, pramas):
    x = np.mat(x).T
    y = x.T * pramas * x
    return np.array(y)

def first_derivative(x, pramas):
    return np.dot((pramas + pramas.T), x)

def second_derivative(x, pramas):
    return pramas + pramas.T

class BaseGradientDescent():
    """base class for Gradient Descent Method
    """
    def __init__(self, pramas, learning_rate, max_iter, epslion):
        self.pramas = pramas
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.epslion = epslion
    
    def _update_location(self, grad):
        self.x = self.x - self.learning_rate * grad
    
    def _initialize(self, x0):
        self.x0 = x0
        self.x = x0
        self.descent_locations = []
    
class NormalGradientDescent(BaseGradientDescent):
    """Gradient Descent Method(estimated extremum)
    
    parameters
    ----------
    pramas : array
        the prama of the target function
    grad_func : function
        the first order derivative of the target function
    learning_rate : float
        the step of in updating location
    max_iter : int
        the max iterations, if iterate over it, break the program
    epslion : float
        the precision, if new gradient less than it, break the program
    
    attributes
    ----------
    x0 : array 
        the start location
    x : array
        the new location by the gradient descent
    descent_locations : list
        save the history of the location
    iter_n : int
        the true counts of the iterations
    """
    
    def __init__(self, pramas, grad_func, learning_rate, max_iter, epslion):
        super(NormalGradientDescent, self).__init__(pramas, learning_rate, 
                                                    max_iter, epslion)
        self.grad_func = grad_func
        
    def _update_location(self, grad):
        """use gradient to update the location
        
        parameters
        ----------
        grad : array
            the gradient
        """
        self.x = self.x - self.learning_rate * grad
        
    def _get_grad(self):
        """get the gradient to update the location
        
        returns
        -------
        grad : array
        """
        grad = self.grad_func(self.x, self.pramas) * self.x
        return grad
    
    def fit(self, x0):
        self._initialize(x0)
        
        for it in range(self.max_iter):
            self.descent_locations.append(self.x)
            
            grad = self._get_grad()
            
            if np.all(np.abs(grad) < self.epslion):
                print('the setting epslion has already been achieved')
                break
            else:
                self._update_location(grad)
        
        self.iter_n = it        
        return self.x
            
class Newton(BaseGradientDescent):
    """Newton Gradient Descent Method(estimated extremum)
    
    parameters
    ----------
    pramas : array
        the prama of the target function
    grad_func1 : function
        the first order derivative of the target function
    grad_func2 : function
        the second order derivative of the target function
    learning_rate : float
        the step of in updating location
    max_iter : int
        the max iterations, if iterate over it, break the program
    epslion : float
        the precision, if new gradient less than it, break the program
    damped : bool
        if Ture, update the learning_rate
        
    attributes
    ----------
    x0 : array 
        the start location
    x : array
        the new location by the gradient descent
    descent_locations : list
        save the history of the location
    iter_n : int
        the true counts of the iterations
    """
    
    def __init__(self, pramas, grad_func1, grad_func2, learning_rate, max_iter, 
                 epslion, damped=False):
        super(Newton, self).__init__(pramas, learning_rate, max_iter, epslion)
        
        self.grad_fun1 = grad_func1
        self.grad_fun2 = grad_func2
        self.damped = damped
        
    def _get_grad(self):
        """get the gradient to update the location
        
        returns
        -------
        grad : array
        """
        grad1 = self.grad_fun1(self.x, self.pramas)
        grad2 = self.grad_fun2(self.x, self.pramas)
        grad = np.ravel(grad1 * np.mat(grad2).I)
        return grad
    
    def _get_learning_rate(self):
        """get the new learning_rate while the damped is Ture
        
        parameters
        ----------
        function y : calculate the new learning_rate
        learning_rate : float
        """
        pass
    
    def fit(self, x0):
        self._initialize(x0)
        
        for it in range(self.max_iter):
            self.descent_locations.append(self.x)
            
            grad = self._get_grad()
            
            if np.all(np.abs(grad) < self.epslion):
                print('the setting epslion has already been achieved')
                break
            else:
                
                if self.damped == True:
                    self._get_learning_rate()
                    
                self._update_location(grad)
        
        self.iter_n = it
        return self.x

class DFP(NormalGradientDescent):
    """DFP Gradient Descent Method(estimated extremum)
    
    parameters
    ----------
    pramas : array
        the prama of the target function
    grad_func : function
        the first order derivative of the target function
    learning_rate : float
        the step of in updating location
    max_iter : int
        the max iterations, if iterate over it, break the program
    epslion : float
        the precision, if new gradient less than it, break the program
    damped : bool
        if Ture, update the learning_rate
        
    attributes
    ----------
    x0 : array 
        the start location
    x : array
        the new location by the gradient descent
    d : array
        the inverse of the Hessian Martix
    descent_locations : list
        save the history of the location
    iter_n : int
        the true counts of the iterations
    """
    
    def __init__(self, pramas, grad_func, learning_rate, max_iter, epslion, 
                 damped=False):
        super(DFP, self).__init__(pramas, grad_func, learning_rate, max_iter, 
                                  epslion)
        
        self.damped = damped
    
    def _get_learning_rate(self):
        pass
    
    def _get_grad(self):
        """get the gradient to update the location
        
        parameters
        ----------
        d : array
            the inverse of Hessian Matrix
        
        returns
        -------
        grad : array
        """
        grad = np.dot(self.d, self.grad_func(self.x, self.pramas))
        return grad
    
    def _get_grad_delta(self, grad1, grad2):
        """get the delta of the latest two gradient
        
        parameters
        ----------
        grad1 : array
            the latest gradient
        grad2 : array
            the second gradient
        
        returns
        -------
        delta : array
            the delta of this two gradients
        """
        delta = grad2 - grad1
        return delta
    
    def _update_inverse_hessian(self, grad, delta):
        """update the inverse of the Hessian Matrix
        
        parameters
        ----------
        grad : array
            the gradient
        delta : array
            the delta of the latest two gradient
        """
        y = np.mat(delta).T
        s = self.learning_rate * np.mat(grad).T
        d = self.d + s * s.T / (s.T * y) - self.d * y * y.T * self.d / (y.T * self.d * y)
        self.d = np.array(d)
        
    def fit(self, x0):
        """the main program of the gradient descent, to find the extremum
        
        parameters
        ----------
        gradients : list
            save the history of the gradient
            
        returns
        -------
        x : the final loaction
        """
        self._initialize(x0)
        self.d = np.eye(x0.shape[0])
        gradients = [0]
        
        for it in range(self.max_iter):
            self.descent_locations.append(self.x)
            grad = self._get_grad()
            gradients.append(grad)
            
            if np.all(np.abs(grad) < self.epslion):
                print('the setting epslion has already been achieved')
                break
            else:
                
                if self.damped == True:
                    self._get_learning_rate()
                
                self._update_location(grad)
                delta = self._get_grad_delta(gradients[-2], gradients[-1])
                self._update_inverse_hessian(grad, delta)
        
        self.iter_n = it
        return self.x
            
class BFGS(DFP):
    """BFGS Gradient Descent Method(estimated extremum)
    
    the whole parameters, attributes and methods of the BFGS are same as the DFP, 
    please check the details in DFP
    """
    def __init__(self, pramas, grad_func, learning_rate, max_iter, epslion, 
                 damped=False):
        super(BFGS, self).__init__(pramas, grad_func, learning_rate, max_iter, 
                                   epslion, damped)
    
    def _update_inverse_hessian(self, grad, delta):
        y = np.mat(delta).T
        s = self.learning_rate * np.mat(grad).T
        i = np.eye(self.d.shape[0])
        d = (i - s * y.T / (y.T * s)) * self.d * (i - y * s.T / (y.T * s)) + s * s.T / (y.T * s)
        self.d = np.array(d)

      
if __name__ == '__main__':
    pramas = np.eye(2)
    learning_rate = 0.1
    max_iter = 100
    epslion = 1e-3
    x0 = np.array([1, 1])
    
    ngd = NormalGradientDescent(pramas, first_derivative, learning_rate, max_iter, epslion)
    ngd.fit(x0)
    
    nt = Newton(pramas, first_derivative, second_derivative, learning_rate, max_iter, epslion)
    nt.fit(x0)
    
    dfp = DFP(pramas, first_derivative, learning_rate, max_iter, epslion)
    dfp.fit(x0)
    
    bfgs = DFP(pramas, first_derivative, learning_rate, max_iter, epslion)
    bfgs.fit(x0)
    