#-*- coding:utf-8 -*-

import random
import math
from operator import itemgetter

class Gene:
    '''
    This is a class to represent individual(Gene) in GA algorithom
    each object of this class have two attribute: data, size
    '''
    def __init__(self,**data):
        self.__dict__.update(data)       
        self.size = len(data['data'])#length of gene
                                
        
class GA:
    '''
    This is a class of GA algorithm. 
    '''
    def __init__(self,parameter):
        '''
        Initialize the pop of GA algorithom and evaluate the pop by computing its' fitness value .
        The data structure of pop is composed of several individuals which has the form like that:
        
        {'Gene':a object of class Gene, 'fitness': 1.02(for example)}

        Representation of Gene is a list: [b s0 u0 sita0 s1 u1 sita1 s2 u2 sita2]
        
        '''
        #parameter = [CXPB, MUTPB, NGEN, popsize, low, up]
        self.parameter = parameter

        low = self.parameter[4]
        up = self.parameter[5]
        
        self.bound = []
        self.bound.append(low)
        self.bound.append(up)
        
        pop = []
        for i in range(self.parameter[3]):
            geneinfo = []
            for pos in range(len(low)):
                geneinfo.append(random.uniform(self.bound[0][pos], self.bound[1][pos]))#initialise popluation
                
            fitness = evaluate(geneinfo)#evaluate each chromosome
            pop.append({'Gene':Gene(data = geneinfo), 'fitness':fitness})#store the chromosome and its fitness
            
        self.pop = pop
        self.bestindividual = self.selectBest(self.pop)#store the best chromosome in the population
        
    def selectBest(self, pop):
        '''
        select the best individual from pop
        '''
        s_inds = sorted(pop, key = itemgetter("fitness"), reverse = False)
        return s_inds[0]
        
    def selection(self, individuals, k):
        '''
        select two individuals from pop
        '''
        s_inds = sorted(individuals, key = itemgetter("fitness"), reverse=True)#sort the pop by the reference of 1/fitness 
        sum_fits = sum(1/ind['fitness'] for ind in individuals) #sum up the 1/fitness of the whole pop
        
        chosen = []
        for i in xrange(k):
            u = random.random() * sum_fits#randomly produce a num in the range of [0, sum_fits]
            sum_ = 0
            for ind in s_inds:
                sum_ += 1/ind['fitness']#sum up the 1/fitness
                if sum_ > u:
                    #when the sum of 1/fitness is bigger than u, choose the one, which means u is in the range of [sum(1,2,...,n-1),sum(1,2,...,n)] and is time to choose the one ,namely n-th individual in the pop
                    chosen.append(ind)
                    break
        
        return chosen    


    def crossoperate(self, offspring):
        '''
        cross operation
        '''
        dim = len(offspring[0]['Gene'].data)

        geninfo1 = offspring[0]['Gene'].data#Gene's data of first offspring chosen from the selected pop
        geninfo2 = offspring[1]['Gene'].data#Gene's data of second offspring chosen from the selected pop
        
        pos1 = random.randrange(1,dim)#select a position in the range from 0 to dim-1, 
        pos2 = random.randrange(1,dim)

        newoff = Gene(data = [])#offspring produced by cross operation
        temp = []
        for i in range(dim):
            if (i >= min(pos1,pos2) and i <= max(pos1,pos2)):
                temp.append(geninfo2[i])
                #the gene data of offspring produced by cross operation is from the second offspring in the range [min(pos1,pos2),max(pos1,pos2)]
            else:
                temp.append(geninfo1[i])
                #the gene data of offspring produced by cross operation is from the frist offspring in the range [min(pos1,pos2),max(pos1,pos2)]
        newoff.data = temp
       
        return newoff


    def mutation(self, crossoff, bound):
        '''
        mutation operation
        '''
        
        dim = len(crossoff.data)

        pos = random.randrange(1,dim)#chose a position in crossoff to perform mutation.

        crossoff.data[pos] = random.uniform(bound[0][pos],bound[1][pos])
        return crossoff
    
    def GA_main(self):
        '''
        main frame work of GA
        '''
        
        popsize = self.parameter[3]
        
        print("Start of evolution")
        
        # Begin the evolution
        for g in range(NGEN):
            
            print("-- Generation %i --" % g)      
                      
            #Apply selection based on their converted fitness
            selectpop = self.selection(self.pop, popsize)   

            nextoff = []    
            while len(nextoff) != popsize:      
                # Apply crossover and mutation on the offspring            
                                
                # Select two individuals
                offspring = [random.choice(selectpop) for i in xrange(2)]
                
                if random.random() < CXPB: # cross two individuals with probability CXPB
                    crossoff = self.crossoperate(offspring)
                    fit_crossoff = evaluate(self.xydata, crossoff.data)# Evaluate the individuals           
                    
                    if random.random() < MUTPB: # mutate an individual with probability MUTPB
                        muteoff = self.mutation(crossoff,self.bound)
                        fit_muteoff = evaluate(self.xydata, muteoff.data)# Evaluate the individuals
                        nextoff.append({'Gene':muteoff,'fitness':fit_muteoff})
                        
            # The population is entirely replaced by the offspring
            self.pop = nextoff
            
            # Gather all the fitnesses in one list and print the stats
            fits = [ind['fitness'] for ind in self.pop]
                
            length = len(self.pop)
            mean = sum(fits) / length
            sum2 = sum(x*x for x in fits)
            std = abs(sum2 / length - mean**2)**0.5
            best_ind = self.selectBest(self.pop)

            if best_ind['fitness'] < self.bestindividual['fitness']:
                self.bestindividual = best_ind

            print("Best individual found is %s, %s" % (self.bestindividual['Gene'].data,self.bestindividual['fitness']))
            print("  Min fitness of current pop: %s" % min(fits))
            print("  Max fitness of current pop: %s" % max(fits))
            print("  Avg fitness of current pop: %s" % mean)
            print("  Std of currrent pop: %s" % std)
        
        print("-- End of (successful) evolution --")    

if __name__ == "__main__":

    CXPB, MUTPB, NGEN, popsize = 0.8, 0.3, 50, 100#control parameters
    
    up = [64, 64, 64, 64, 64, 64, 64, 64, 64, 64]#upper range for variables
    low = [-64, -64, -64, -64, -64, -64, -64, -64, -64, -64]#lower range for variables
    parameter = [CXPB, MUTPB, NGEN, popsize, low, up]
    
    run = GA(parameter)
    run.GA_main()