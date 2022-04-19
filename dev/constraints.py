### PPFS and budget lines class PPF(LinearConstraint):
import matplotlib.pyplot as plt
import numpy as np

class LinearConstraint:
    def __init__ (self, p1 = None, p2 = None, max1 = None, max2 = None, endowment = 1,
                 good_names = ['Good 1', 'Good 2']):
        """Create a linear budget line or PPF."""
        
        self.good_names = good_names
        if (p1 != None):
            self.p1 = p1
            self.max1 = endowment / p1
        elif (max1 != None):
            self.p1 = endowment / max1
            self.max1 = max1
        else:
            print('add error handling')
          
        if p2 != None:
            self.p2 = p2
            self.max2 = endowment / p2

        elif (max2 != None):
            self.p2 = endowment / max2
            self.max2 = max2
        else:
            print('add error handling')
            
        self.endowment = endowment
            
            
            
        
    def plot(self, ax = None, linewidth = 2):
        if ax == None:
            ax = plt.gca()
            
        ax.plot([0,self.max1], [self.max2, 0], linewidth = linewidth)
        
        ax.set_xlabel(self.good_names[0])
        ax.set_ylabel(self.good_names[1])
        
        
        if True:
            ax.spines['left'].set_position('zero')
            ax.spines['bottom'].set_position('zero')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False) 
        
    
class PPF(LinearConstraint):

    def __init__ (self ,p1 = None, p2 = None, max1 = None, max2 = None, endowment = 1,
                 good_names = ['Good 1', 'Good 2']):
        """Create demand curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P).""" 
        LinearConstraint.__init__(self, p1, p2, max1, max2, endowment,
                 good_names)
        
class JointPPF:
    
    
    def __init__ (self, ppf_array):
        """Create a joint PPF from two linear PPFs. Requires equal endowment."""
        
        ppf1 = ppf_array[0]
        ppf2 = ppf_array[1]
        self.ppf_array = ppf_array
        
        same_endowment = ppf1.endowment == ppf2.endowment
    
        if not same_endowment:
            #overwrite ppf2 with ppf1 endowment
            ppf2 = PPF(p1 = ppf2.p1, p2 = ppf2.p2, endowment = ppf1.endowment)
            
        self.endowment = ppf1.endowment
        
        for key, ppf in enumerate(ppf_array):
            self.__dict__['ppf'+ str(key)] = ppf
            
        #self.ppf1 = ppf1
        #self.ppf2 = ppf2
        
        # figure out comparative advantages
        # who has lowest cost of good 1? 
        
        # relative price, absolute price, and index in ppf_array
        good1_opp_costs = sorted([(ppf.p1/ppf.p2, ppf.p1, key) for (key, ppf) in enumerate(ppf_array)])
        
        self.good1_opp_costs = good1_opp_costs
        
        good2_intercept = np.sum([ppf.max2 for ppf in ppf_array])
        good1_intercept = np.sum([ppf.max1 for ppf in ppf_array])

        # three points
        self.intercept2 = good2_intercept
        self.intercept1 = good1_intercept
        
        kinks = list()
        
        total_lost2 = 0
        total_made1 = 0
        for opp_cost, cost, key in good1_opp_costs:
            
            # how much good1 made
            made1 = ppf_array[key].max1 #endowment / cost
            lost2 = ppf_array[key].max2
            
            total_lost2 += lost2
            total_made1 += made1
            kink = (total_made1, good2_intercept - total_lost2)
            
            if good2_intercept - total_lost2 > 0:
                kinks.append(kink)
            
        self.kinks = kinks
        
        #if ppf2.p2 <= ppf1.p1: # arbitrary tiebreaker
         #   comp_adv2 = 'ppf2'
          #  comp_adv1 = 'ppf1'
        #else:
         #   comp_adv2 = 'ppf1'
          #  comp_adv1 = 'ppf2'

        #self.comp_adv1 = comp_adv1
        #self.comp_adv2 = comp_adv2

      

        #self.kink = self.__dict__[comp_adv1].max1, self.__dict__[comp_adv2].max2
    
    def plot(self, ax = None, title = 'Joint PPF'):
        if ax == None:
            ax = plt.gca()
        
        # intercept 2 to kink
        
        prev_kink = (0, self.intercept2)
        for key, kink in enumerate(self.kinks):
            
            
            ax.plot([prev_kink[0],kink[0]], [prev_kink[1], kink[1]], color = 'black')

            
            # marker at kink
            ax.plot([kink[0]], [kink[1]], marker = 'o')
            ax.plot([kink[0], kink[0]], [0, kink[1]], linestyle = 'dashed', color = 'C0')
            ax.plot([0, kink[0]], [kink[1], kink[1]], linestyle = 'dashed', color = 'C0')

            # kink to intercept 1

            if key+1 == len(self.kinks):
                ax.plot([kink[0], self.intercept1], [kink[1], 0], color = 'black')
        
            prev_kink = kink
        if True:
            ax.spines['left'].set_position('zero')
            ax.spines['bottom'].set_position('zero')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False) 
        
        ax.set_xlabel(self.ppf_array[0].good_names[0])
        ax.set_ylabel(self.ppf_array[0].good_names[1])
        ax.set_title(title)
        
        # label just the important points
        
        important_x = [self.intercept1] + [kink[0] for kink in self.kinks]
        important_y = [0, self.intercept2] + [kink[1] for kink in self.kinks]
        
        ax.set_xticks(important_x)
        ax.set_yticks(important_y)
        
    def efficiency(self, good1, good2):
        """Return if a point is inefficient, efficient, or unattainable."""
    
        # let comp_adv for good 1 make good 1
        
        endowment = self.ppf1.endowment
        #good1_ppf = self.__dict__[self.comp_adv1]
        #good2_ppf = self.__dict__[self.comp_adv2]
        
        # comp adv in good1, descending
        comp_adv_order = [self.ppf_array[x[2]] for x in self.good1_opp_costs]
        
        #p1 = good1_ppf.p1
        #p2 = good2_ppf.p2
        
        # make good 1
        good1_made = 0
        left = good1 - good1_made
        comp_adv_index = -1
        
        while left > 0:
            comp_adv_index += 1
            ppf = comp_adv_order[comp_adv_index]
            
            time_nec = left/ppf.p1
            contribution = np.min([time_nec/ppf.p1, endowment/ppf.p1])
            
            time_left = np.max([0,endowment - time_nec])
            left -= contribution
            
        if good1 == 0:
            time_left = endowment
            comp_adv_index = 0
        
        # make good 2
        good2_left  = good2
        for ppf in comp_adv_order[comp_adv_index:]:
            
            contribution = time_left / ppf.p2
            
            good2_left -= contribution
            # change time left to endowment for non-transitional ppfs for next iterations
            time_left = endowment
            
        if good2_left < 0:
            return "inefficient"
        elif good2_left == 0:
            return 'efficient'
        else:
            return "unattainable"

      
