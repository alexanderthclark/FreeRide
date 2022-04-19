############################################################
#### Equilibrium Classes
import numpy as np

class Equilibrium:
    
    def __init__ (self, demand, supply):
        """Equilibrium produced by demand and supply. Initialized as market equilibrium."""
        # check types
        
        objs = demand, supply
        types = type(demand).__name__, type(supply).__name__
        if 'Demand' not in types:
            raise TypeError("Missing Demand object")
        if 'Supply' not in types:
            raise TypeError("Missing Supply object")
            
        # flexibility if demand and supply arguments are reversed
        demand = objs[types.index('Demand')]
        supply = objs[types.index('Supply')]
        self.demand = demand
        self.supply = supply
                
        # Solve for equilibrium
        v1 = np.array([1, -demand.slope])
        v2 = np.array([1, -supply.slope])
        b = demand.intercept, supply.intercept
        A = np.array((v1, v2))
        b = np.array(b).T

        x = np.matmul(np.linalg.inv(A), b).squeeze()
        self.p, self.market_p = x[0], x[0]
        self.q, self.market_q = x[1], x[1]
        
        
        # initialize other things
        # these are hidden attributes
        self.__tax = 0
        self.__subsidy = 0
        self.__p_consumer = self.p
        self.__p_producer = self.p
        self.__dwl = 0
        self.__externalities = False
        

    def plot(self, ax = None, annotate = False, clean = True,
            fresh_ticks = True):
        
        if ax == None:
            fig, ax = plt.subplots()
                
        # plot the curves
        for curve in self.demand, self.supply:
            curve.plot(ax = ax)
            
        # dashed lines
        q, p = self.q, self.p # p can be a tuple 

        if type(p) != tuple:

            ax.plot([0,q], [p,p],
                      linestyle = 'dashed', color = 'C0')
            ax.plot([q,q], [0,p],
                      linestyle = 'dashed', color = 'C0')
            ax.plot([q], [p], marker = 'o')

        else:
            
            # vertical line
            max_p = np.max(p)
            ax.plot([q,q], [0, max_p],
                      linestyle = 'dashed', color = 'C0')

            # horizontal lines
            for p_ in p:
                ax.plot([0,q], [p_, p_],
                      linestyle = 'dashed', color = 'C0')
                ax.plot([q], [p_], marker = 'o')

        # annotation
        if annotate:
            s = " $p = {:.1f}, q = {:.1f}$".format(p,q)
            ax.text(q,p, s, ha = 'left')
            
        ax.set_ylabel("Price")
        ax.set_xlabel("Quantity")
        
        if clean:
            self.plot_clean(ax, fresh_ticks = fresh_ticks)
            
    def plot_clean(self, ax = None, fresh_ticks = True, axis_arrows = True):
        """Clean Equilibrium plot."""
        if ax == None:
            ax = plt.gca()
            
        # check previous ticks
        prev_x = set(ax.get_xticks())
        prev_y = set(ax.get_yticks())
        
        # label only important points on axes
        important_y = np.min(self.p), np.max(self.p), self.demand.intercept
        important_y = sorted(list(set(important_y))) # if p not a tuple
        important_x = self.q, self.demand.q_intercept
        
        if self.supply.intercept >= 0:
            important_y = self.supply.intercept, *important_y
        if self.supply.q_intercept > 0:
            important_x = self.supply.q_intercept, *important_x
        
        combined_xticks = set(important_x).union(prev_x)
        combined_yticks = set(important_y).union(prev_y)
        

        if fresh_ticks:
            ax.set_xticks([round(x,2) for x in important_x if not np.isnan(x)])
            ax.set_yticks([round(x,2) for x in important_y if not np.isnan(x)])
        else:
            ax.set_xticks(sorted(list([round(x,2) for x in combined_xticks if not np.isnan(x)])))
            ax.set_yticks(sorted(list([round(x,2) for x in combined_yticks if not np.isnan(x)])))
                
        # set limits
        x_int = self.demand.q_intercept*1.04
        if np.isnan(x_int):
            x_int = 2*self.q

        ax.set_xlim(0, x_int)
        ax.set_ylim(0, self.demand.intercept*1.04)
        
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        
        
        # label demand and supply curves
        
        # remove existing labels
        texts = ax.texts
        for t in texts[::-1]:
            if t.get_text() in 'DS':
                t.remove()
                
        # add demand label
        y_delta = (ylims[1]-ylims[0])/30
        max_x = xlims[1]
        max_q_int = self.demand.q_intercept
        q_val = np.min([max_x, max_q_int]) * 0.95
        ax.text(q_val, self.demand.p(q_val) + y_delta*.99, 'D', size = 14)
        
        # add supply label
        y1 = self.supply.p(q_val)
        if y1 > ylims[1]:
            q_val = self.supply.q(ylims[1]*.95)
        ax.text(q_val, self.supply.p(q_val) + y_delta*1.03, 'S', size = 14)

        
        # Add arrows to axes
        if axis_arrows:
            ax.plot(xlims[1], 0, ">k", clip_on = False)
            ax.plot(0, ylims[1], "^k", clip_on = False)
            
    def surplus(self):
        """Returns producer surplus, consumer surplus, government revenue.
        Negative government revenue indicates government expenditure."""
        ps = self.supply.producer_surplus(e.p_producer)
        cs = self.demand.consumer_surplus(e.p_consumer)
        # Govt revenue
        govt = (self.tax - self.subsidy) * self.q

        return ps, cs, govt
