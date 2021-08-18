class Curve:

    def __init__ (self, a, b, inverse = True):
        
        if inverse:
            self.intercept = a
            self.slope = b
            self.q_intercept = -a/b
            
        else:
            self.slope = 1/b
            self.intercept = -a/b
            self.q_intercept = a
    
    def q(self, p):
        """Quantity demanded at price p."""
        return (self.intercept/(-self.slope)) + (p/self.slope)
    
        
    def vertical_shift(self, delta):
        """Shift curve vertically by amount delta."""
        self.intercept += delta   
        
    def horizontal_shift(self, delta):
        """Shift curve horizontall by amount delta."""
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
        Curve.__init__(self, a, b, inverse)

    def consumer_surplus(self, p):
        
        tri_height = self.intercept - p
        tri_base = self.q(p)
        
        return 0.5 * tri_base * tri_height
    
    def plot_surplus(self, supply, ax = ax, annotate = False):
        
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
        
    def plot_surplus(self, demand, ax = ax, annotate = False):
        
        p,q = self.equilibrium(demand)
        
        # CS region
        cs_plot = ax.fill_between([0,q], y1 = [demand.intercept, p], y2 = p,  alpha = 0.1)
        
        # fix later for negative 
        ps_plot = ax.fill_between([0,q], y1 = [self.intercept, p], y2 = p, color = 'C1', alpha = 0.1)
        
        if annotate:
            cs = demand.consumer_surplus(p)
            ps = self.producer_surplus(p)
            
            
class Equilibrium:
    
    def __init__ (self, demand, suply):
       
        p, q = demand.equilibrium(supply)
        self.p = p
        self.q = q
        
    def plot(self, ax):
        
        demand.equilibrium_plot(supply, ax = ax)
        
    def plot_clean(self, ax):
        
        demand.equilibrium_plot_cleaner(supply, ax)
        
    def plot_surplus(self, ax):
        
        p,q = self.p, self.q
        
        # CS region
        cs_plot = ax.fill_between([0,q], y1 = [demand.intercept, p], y2 = p,  alpha = 0.1)
        
        # fix later for negative 
        ps_plot = ax.fill_between([0,q], y1 = [self.intercept, p], y2 = p, color = 'C1', alpha = 0.1)
        