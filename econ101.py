# new stuff

import numpy as np
import matplotlib.pyplot as plt

class Curve:

    def __init__ (self, intercept, slope, inverse = True):
        """Create curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P)."""
        if inverse:
            self.intercept = intercept
            self.slope = slope
            self.q_intercept = -intercept/slope
            
        else:
            self.slope = 1/slope
            self.intercept = -intercept/slope
            self.q_intercept = intercept
    
    def q(self, p):
        """Quantity demanded or supplied at price p."""
        return (self.intercept/(-self.slope)) + (p/self.slope)
    
        
    def vertical_shift(self, delta):
        """Shift curve vertically by amount delta."""
        self.intercept += delta   
        
    def horizontal_shift(self, delta):
        """Shift curve horizontally by amount delta."""
        equiv_vert = delta * -self.slope
        self.intercept += equiv_vert        

    def equilibrium(self, other_curve):
        """Returns a tuple (p, q)."""
        
        v1 = np.array([1, -self.slope])
        v2 = np.array([1, -other_curve.slope])
        
        b = self.intercept, other_curve.intercept

        A = np.matrix((v1, v2))
        b = np.matrix(b).T

        x = np.linalg.inv(A) * b
        x = x.squeeze()
        return x[0,0], x[0,1] # p, q
    
    #make this hidden
    def plot(self, ax, color = 'black', max_q = 10):
        
        # core plot
        x2 = np.max([self.q_intercept, max_q])
        y2 = self.intercept + self.slope * x2
        
        xs = np.linspace(0, x2,2)
        ys = np.linspace(self.intercept, y2, 2)
        
        ax.plot(xs, ys, color = color)
        
        # set lims
        if self.slope > 0:
            top = self.intercept*2 + 10 *(self.intercept == 0)
        else:
            top = self.intercept * 1.1
            
        #ax.set_ylim(0,top)
        
        #return xs, ys
    
    
    
    def equilibrium_plot(self, other_curve, ax = None, annotate = True):
        """Plot the intersection of two curves."""
        if ax == None:
            fig, ax = plt.subplots()
        #else:
         #   global ax
        for curve in self, other_curve:
            curve.plot(ax = ax)
            
        ax.set_ylabel("Price")
        ax.set_xlabel("Quantity")
        
        
        ## annotate equilibrium
        
        if annotate:
            p, q = self.equilibrium(other_curve)

            ax.plot([0,q], [p,p],
                      linestyle = 'dashed', color = 'C0')
            ax.plot([q,q], [0,p],
                      linestyle = 'dashed', color = 'C0')
            ax.plot([q], [p], marker = 'o')

            s = "$p = {:.1f}, q = {:.1f}$".format(p,q)

            ax.text(q,p, s, ha = 'left')
  
        
    # elasticity section
    
    def price_elasticity(self, p):
        """Find point price elasticity given a price."""
        
        q = self.q_intercept + (1/self.slope) * p
        e = (p/q) * (1/self.slope)
        return e
        
        #return q
        
    def midpoint_elasticity(self, p1, p2):
        """Find price elasticity between two prices, using the midpoint formula. """
        mean_p = 0.5*p1 + 0.5*p2
        return self.price_elasticity(mean_p)
  
        
    def equilibrium_plot_cleaner(self, other_curve, ax):
        
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # customize limits 
        
        # P-axis intercepts (y-axis)
        min_int = np.min([self.intercept, other_curve.intercept])
        max_int = np.max([self.intercept, other_curve.intercept])

        min_y = np.min([-1, min_int])
        max_y = np.max([0, max_int*1.1])
        ax.set_ylim(min_y, max_y)
        
        # Q-axis intercepts (x-axis)
        min_int = np.min([self.q_intercept, other_curve.q_intercept])
        max_int = np.max([self.q_intercept, other_curve.q_intercept])

        min_x = np.min([-1, min_int])
        max_x = np.max([0, max_int*1.1])
        ax.set_xlim(min_x, max_x)
        
        
        
        
            
class Demand(Curve):

    def __init__ (self , a , b , inverse = True):
        """Create demand curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P).""" 
        Curve.__init__(self, a, b, inverse)

    def consumer_surplus(self, p):
        
        tri_height = self.intercept - p
        tri_base = self.q(p)
        
        return 0.5 * tri_base * tri_height
    
    def plot_surplus(self, supply, ax, annotate = False):
        
        p,q = self.equilibrium(supply)
        
        # CS region
        cs_plot = ax.fill_between([0,q], y1 = [self.intercept, p], y2 = p,  alpha = 0.1)
        
        # fix later for negative 
        ps_plot = ax.fill_between([0,q], y1 = [supply.intercept, p], y2 = p, color = 'C1', alpha = 0.1)
        
        if annotate:
            cs = self.consumer_surplus(p)
            ps = supply.producer_surplus(p)
    
class Supply(Curve):

    def __init__ (self , a , b , inverse = True):
        """Create supply curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P).""" 
        Curve.__init__(self, a, b, inverse)
  
    def producer_surplus(self, p):
        
        qs = self.q(p)
        
        if qs <= 0:
            return 0
    
        if self.intercept >= 0:
        
            tri_height =  - self.intercept + p
            tri_base = qs

            ps1 = 0.5 * tri_base * tri_height

            return ps1
        
        # get rectangle
        rect_w = self.q_intercept
        rect_h = p
        rect_area = rect_w * rect_h
        
        tri_area = 0.5 * (qs - rect_w) * p
        
        return tri_area + rect_area
        
    def plot_surplus(self, demand, ax, annotate = False):
        
        p,q = self.equilibrium(demand)
        
        # CS region
        cs_plot = ax.fill_between([0,q], y1 = [demand.intercept, p], y2 = p,  alpha = 0.1)
        
        # fix later for negative 
        ps_plot = ax.fill_between([0,q], y1 = [self.intercept, p], y2 = p, color = 'C1', alpha = 0.1)
        
        if annotate:
            cs = demand.consumer_surplus(p)
            ps = self.producer_surplus(p)
            
            
class Equilibrium:
    
    def __init__ (self, demand, supply):
        """Equilibrium produced by demand and supply."""
        p, q = demand.equilibrium(supply)
        self.p = p
        self.q = q
        self.demand = demand
        self.supply = supply
        self.tax = 0
        self.subsidy = 0
        self.p_consumer = self.p
        self.p_producer = self.p
        self.dwl = 0
        self.externalities = False
        
    def plot(self, ax):
        
        if self.tax == 0:
            self.demand.equilibrium_plot(self.supply, ax = ax)
        else:
            pass
        
    def plot_clean(self, ax):

        self.demand.equilibrium_plot_cleaner(self.supply, ax)
        
        # label only important points
        important_y = self.p, self.demand.intercept
        important_x = self.q, self.demand.q_intercept
        
        if self.supply.intercept >= 0:
            important_y = self.supply.intercept, *important_y
        if self.supply.q_intercept > 0:
            important_x = self.supply.q_intercept, *important_x
        
        ax.set_xticks(important_x)
        ax.set_yticks(important_y)

        # label demand and supply curves
        # not written yet

        # set limits
        ax.set_xlim(0, self.demand.q_intercept*1.04)
        ax.set_ylim(0, self.demand.intercept*1.04)
        
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        
        # Add arrows to axes
        ax.plot(xlims[1], 0, ">k", clip_on = False)
        ax.plot(0, ylims[1], "^k", clip_on = False)

        
    def plot_surplus(self, ax, annotate = True):
        
        p,q = self.p, self.q
        
        # CS region
        cs_plot = ax.fill_between([0,q], y1 = [self.demand.intercept, p], y2 = p,  alpha = 0.1)
        
        # fix later for negative 
        ps_plot = ax.fill_between([0,q], y1 = [self.supply.intercept, p], y2 = p, color = 'C1', alpha = 0.1)
        
        if annotate:
            x_pos = self.q/3

            # meean between price and along supply curve
            ps_y = np.mean([self.p_producer, self.supply.intercept + self.supply.slope * x_pos])
            
            cs_y = np.mean([self.p_consumer, self.demand.intercept + self.demand.slope * x_pos])

            ax.text(x_pos, cs_y, 'CS', ha = 'center', va = 'center')
            ax.text(x_pos, ps_y, 'PS', ha = 'center', va = 'center')
        
    def set_tax(self, tax):
        """Impose a per-unit tax."""
        
        self.tax = tax
        
        self.distortion = self.tax / (self.supply.slope - self.demand.slope)
        
        # update q relative to market quantity
        self.q = self.demand.equilibrium(self.supply)[1] - self.distortion
        
        self.p_consumer = self.demand.intercept + self.demand.slope * self.q
        self.p_producer = self.supply.intercept + self.supply.slope * self.q
        
        if self.q < 0:
            self.q = 0
            
        if self.p_consumer != self.p_producer:
            self.p = self.p_consumer, self.p_producer
        else:
            self.p = self.p_consumer
            
        self.dwl = np.abs(self.distortion * self.tax * 0.5)
        
    def set_subsidy(self, subsidy):
        """Impose a per-unit subsidy."""
        self.subsidy = subsidy
        self.set_tax(-subsidy)
        self.distortion = -self.distortion