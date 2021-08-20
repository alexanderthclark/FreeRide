
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
    def p(self, q):
        """Price when quantity demanded/supplied is at q."""
        return self.intercept + self.slope * q

        
    def vertical_shift(self, delta):
        """Shift curve vertically by amount delta. Shifts demand curve to the right.
        Shifts supply curve to the left."""
        self.intercept += delta
        self.q_intercept = -self.intercept / self.slope
        
    def horizontal_shift(self, delta):
        """Shift curve horizontally by amount delta. Positive values are shifts to the right."""
        equiv_vert = delta * -self.slope
        self.intercept += equiv_vert  
        self.q_intercept = -self.intercept / self.slope


    def equilibrium(self, other_curve):
        """Returns a tuple (p, q). Allows for negative prices or quantities."""
        
        v1 = np.array([1, -self.slope])
        v2 = np.array([1, -other_curve.slope])
        
        b = self.intercept, other_curve.intercept

        A = np.matrix((v1, v2))
        b = np.matrix(b).T

        x = np.linalg.inv(A) * b
        x = x.squeeze()
        return x[0,0], x[0,1] # p, q
    

    def plot(self, ax = None, color = 'black', linewidth = 2, max_q = 10):
        
        if ax == None:
            ax = plt.gca()

        # core plot
        x2 = np.max([self.q_intercept, max_q])
        y2 = self.intercept + self.slope * x2
        
        xs = np.linspace(0, x2,2)
        ys = np.linspace(self.intercept, y2, 2)
        
        ax.plot(xs, ys, color = color, linewidth = linewidth)
    
    
    
    def equilibrium_plot(self, other_curve, ax = None, linewidth = 2, annotate = False):
        """Plot the intersection of two curves. This can't handle taxes or other interventions."""
        if ax == None:
            fig, ax = plt.gcf(), plt.gca()
        #else:
         #   global ax
        for curve in self, other_curve:
            curve.plot(ax = ax, linewidth = linewidth)
            
        ax.set_ylabel("Price")
        ax.set_xlabel("Quantity")
        
        # dashed lines around market price and quantity
        p, q = self.equilibrium(other_curve)
        ax.plot([0,q], [p,p],
                  linestyle = 'dashed', color = 'C0')
        ax.plot([q,q], [0,p],
                  linestyle = 'dashed', color = 'C0')
        ax.plot([q], [p], marker = 'o')

        # annotation on the plot
        if annotate:
            s = " $p = {:.1f}, q = {:.1f}$".format(p,q)
            ax.text(q,p, s, ha = 'left', va = 'center')
  
        
    # elasticity section
    
    def price_elasticity(self, p):
        """Find point price elasticity given a price."""
        
        q = self.q_intercept + (1/self.slope) * p
        e = (p/q) * (1/self.slope)
        return e
       
        
    def midpoint_elasticity(self, p1, p2):
        """Find price elasticity between two prices, using the midpoint formula. """
        mean_p = 0.5*p1 + 0.5*p2
        return self.price_elasticity(mean_p)
  
        
    def equilibrium_plot_cleaner(self, other_curve, ax = None):
        
        if ax == None:
            ax = plt.gca()

        # Make textbook-style plot window
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

    def externality(self, externality, is_signed = True, is_positive = None):
        """Creates marginal social cost or benefit given a Curve and externality."""

        is_demand = self.slope < 0 # figure out if this is supply or demand curve

        if is_positive == True: # add to demand/MSB, substract from supply MSC
            if is_demand:
                externality = np.abs(externality)
            else:
                externality = - np.abs(externality)
        if is_positive == False
            if is_demand:
                externality =  - np.abs(externality)
            else:
                externality = + np.abs(externality)


        social_curve = Curve(self.intercept + self.externalitiy, self.slope, inverse = True)
        return social_curve

        
class Aggregate:

    def __init__ (self, curve_array = None, *args):
        """Create aggregated supply or demand curves. Arguments must be all supply or all demand."""
 
        #self.__dict__.update(('curve' + str(k), v) for k, v in enumerate(curve_array))
        if (curve_array == None):
            curve_array = list(args)
        self.curve_array = curve_array
        slopes = sorted([x.slope for x in self.curve_array])
        self.is_demand = slopes[0] < 0
        self.is_supply = not self.is_demand
        
    def q(self, p):
        """Find aggregate quantity at price p."""
        total_q = 0
        for curve in self.curve_array:
            total_q += np.max([0,curve.q(p)])
        return total_q

    def plot(self, ax = None, color = 'black', linewidth = 2, max_q = 10):
        
        if ax == None:
            ax = plt.gca()


        intercepts = sorted([x.intercept for x in self.curve_array])
        slopes = sorted([x.slope for x in self.curve_array])
        
        if np.min(slopes) < 0: # demand curves

            max_y = intercepts[-1]

            y_vec = np.linspace(0,max_y, 1000)
            x_vec = [self.q(y) for y in y_vec]

            ax.plot(x_vec, y_vec, color = color, linewidth = linewidth)
        else: # supply curve

            max_y = intercepts[-1]*2
            y_vec = np.linspace(0,max_y, 1000)
            x_vec = [self.q(y) for y in y_vec]

            ax.plot(x_vec, y_vec, color = color, linewidth = linewidth)


    def kinks(self):
        """Return p, q pairs for kink locations."""
        intercepts = sorted([x.intercept for x in self.curve_array])
        pairs = list()

        if self.is_demand == True:
            relevant_intercepts = intercepts[:-1]
        else:
            relevant_intercepts = intercepts[1:]
        for intercept in relevant_intercepts:
            # get q
            q = self.q(intercept)
            pair = [(intercept, q)] 
            pairs += pair
        return pairs

    def plot_clean(self, ax = None):

        if ax == None:
            ax = plt.gca()

        kink_list = self.kinks()

        ys = [pair[0] for pair in kink_list] # p values
        xs = [pair[1] for pair in kink_list] # q values

        intercepts = sorted([x.intercept for x in self.curve_array])

        important_x = xs + [self.q(0)]
        important_x = [x for x in sorted(important_x) if x > 0]

        important_y = ys + intercepts
        important_y = [0] + [y for y in sorted(important_y) if y > 0]

        ax.set_yticks(important_y)
        ax.set_xticks(important_x)

        # Make textbook-style plot window
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    def equilibrium(self, other, price_guess = 1, tolerance = .05):
        """Find market clearing price and quantity with another aggregate or curve object."""

        surplus = self.q(price_guess) - other.q(price_guess)
        if self.is_demand:
            excess_demand = surplus
        else:
            excess_demand = -surplus 

        has_cycled = False
        counter, last_counter = 0, 0
        scale = 1
        while np.abs(excess_demand) > tolerance:

            if excess_demand > 0: 

                price_guess += tolerance * scale

                if counter > last_counter:
                    has_cycled = True
                    scale *= 0.5
                counter += 1
                last_counter = counter
            else: # must be strictly negative bc while condition

                price_guess -= tolerance
                counter += 1
            #print(price_guess, surplus)
            surplus = self.q(price_guess) - other.q(price_guess)
            if self.is_demand:
                excess_demand = surplus
            else:
                excess_demand = -surplus 

        # get points on supply and demand 
        # use local linearity to find exact solution
        #p1 = price_guess, self.q(price_guess)
        #p2 = price_guess, self.q(price_guess)

        # returns point on the object on which the method is called
        return price_guess, self.q(price_guess)

    def equilibrium_plot(self, other, ax = None):
        if ax == None:
            ax = plt.gca()

        # plot curves
        self.plot(ax)
        other.plot(ax)


        # add equilibrium things
        p, q = self.equilibrium(other)

        # reset ticks and such
       
        kink_list = self.kinks() + other.kinks()

        ys = [pair[0] for pair in kink_list] # p values
        xs = [pair[1] for pair in kink_list] # q values

        intercepts = sorted([x.intercept for x in self.curve_array])

        important_x = xs + [self.q(0)] + [q]
        important_x = [x for x in sorted(important_x) if x > 0]

        important_y = ys + intercepts + [p]
        important_y = [0] + [y for y in sorted(important_y) if y > 0]

        #ax.set_yticks(important_y)
        #ax.set_xticks(important_x)

        # label p and q
        ax.plot([0,q], [p,p], linestyle = 'dashed', color = 'C0')
        ax.plot([q,q], [0,p], linestyle = 'dashed', color = 'C0')

        # set axes limits 
        if self.is_demand:
            self.plot_clean()
            xmax = self.q(0)
            ymax = ax.get_yticks()[-1]
        else:
            #other.plot_clean()
            xmax = other.q(0)
            ymax = other.get_yticks()[-1]

        ax.set_xlim(0, xmax*1.04)
        ax.set_ylim(0, ymax*1.04)

        ax.set_yticks(important_y)
        ax.set_xticks(important_x)
        return important_x, important_y


            
class Demand(Curve):
    """Creates linear, downward-sloping demand curve."""

    def __init__ (self , intercept, slope, inverse = True):
        """Create demand curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P).""" 
        Curve.__init__(self, intercept, slope, inverse)

    def consumer_surplus(self, p):
        """Calculate consumer surplus given a price p."""
        tri_height = self.intercept - p
        tri_base = self.q(p)
        
        return 0.5 * tri_base * tri_height
    
    def plot_surplus(self, p, ax = None):
        """Plot consumer surplus."""

        if ax == None:
            ax = plt.gca()

        # CS region
        cs_plot = ax.fill_between([0,q], y1 = [self.intercept, p], y2 = p,  alpha = 0.1)
        
    
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
        
    def plot_surplus(self, demand, ax = None, annotate = False):
        
        #p,q = self.equilibrium(demand)
        if ax == None:
            ax = plt.gca()
        # CS region
        #cs_plot = ax.fill_between([0,q], y1 = [demand.intercept, p], y2 = p,  alpha = 0.1)
        
        # fix later for negative 
        ps_plot = ax.fill_between([0,q], y1 = [self.intercept, p], y2 = p, color = 'C1', alpha = 0.1)
        
        #if annotate:
         #   cs = demand.consumer_surplus(p)
          #  ps = self.producer_surplus(p)
            
            
class Equilibrium:
    
    def __init__ (self, demand, supply):
        """Equilibrium produced by demand and supply. Initialized as market equilibrium."""
        p, q = demand.equilibrium(supply)
        self.p, self.market_p = p, p
        self.q, self.market_q = q, q
        self.demand = demand
        self.supply = supply
        self.tax = 0
        self.subsidy = 0
        self.p_consumer = self.p
        self.p_producer = self.p
        self.dwl = 0
        self.externalities = False
        
    def plot(self, ax = None, annotate = False, clean = True, fresh_ticks = True):
        if ax == None:
            ax = plt.gca()
        if self.p_producer == self.p_consumer:
            self.demand.equilibrium_plot(self.supply, ax = ax, annotate = annotate)
        else:
            pass
        
        if clean:
            self.plot_clean(ax, fresh_ticks = fresh_ticks)
            
    def plot2(self, ax = None, annotate = False, clean = True, fresh_ticks = True):

        """Plot the intersection of two curves."""
        if ax == None:
            fig, ax = plt.subplots()
        #else:
         #   global ax
        for curve in self.demand, self.supply:
            curve.plot(ax = ax)

        ax.set_ylabel("Price")
        ax.set_xlabel("Quantity")

        # dashed lines
        q, p = self.q, self.p # p can be a tuple 

        if type(p) != tuple:

            ax.plot([0,q], [p,p],
                      linestyle = 'dashed', color = 'C0')
            ax.plot([q,q], [0,p],
                      linestyle = 'dashed', color = 'C0')
            ax.plot([q], [p], marker = 'o')

        else:

            max_p = np.max(p)
            ax.plot([q,q], [0, max_p],
                      linestyle = 'dashed', color = 'C0')

            for p_ in p:
                ax.plot([0,q], [p_, p_],
                      linestyle = 'dashed', color = 'C0')

                ax.plot([q], [p_], marker = 'o')

        # annotation
        if annotate:
            s = " $p = {:.1f}, q = {:.1f}$".format(p,q)
            ax.text(q,p, s, ha = 'left')

        if clean:
            self.plot_clean(ax, fresh_ticks = fresh_ticks)
        
    def plot_clean(self, ax = None, fresh_ticks = True, axis_arrows = False):

        if ax == None:
            ax = plt.gca()
            
        # Changes spine styling and sets limits (again reset below)
        self.demand.equilibrium_plot_cleaner(self.supply, ax)
        
        
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
            ax.set_xticks(important_x)
            ax.set_yticks(important_y)
        else:
            ax.set_xticks(sorted(list(combined_xticks)))
            ax.set_yticks(sorted(list(combined_yticks)))

        # label demand and supply curves
        # not written yet

        # set limits
        ax.set_xlim(0, self.demand.q_intercept*1.04)
        ax.set_ylim(0, self.demand.intercept*1.04)
        
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        
        if axis_arrows:
            # Add arrows to axes
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
        
    def plot_surplus(self, ax = None, annotate = True):
        
        if ax == None:
            ax = plt.gca()
        
        p,q = self.p, self.q
        
        # CS region
        cs_plot = ax.fill_between([0,q], y1 = [self.demand.intercept, self.p_consumer], 
            y2 = self.p_consumer, 
            alpha = 0.1)
        
        # fix later for negative 
        ps_plot = ax.fill_between([0,q], y1 = [self.supply.intercept, self.p_producer], 
            y2 = self.p_producer, 
            color = 'C1', alpha = 0.1)
        
        high_price, low_price = np.max(p), np.min(p)
        g_plot = ax.fill_between([0,q], y1 = high_price, y2 = low_price,
            color = 'C2', alpha = 0.1)

        if annotate:
            x_pos = self.q/3

            # meean between price and along supply curve
            ps_y = np.mean([self.p_producer, self.supply.intercept + self.supply.slope * x_pos])
            
            cs_y = np.mean([self.p_consumer, self.demand.intercept + self.demand.slope * x_pos])

            govt_y = np.mean(p)

            if type(p) == tuple:
                ax.text(self.q/4, govt_y, 'Govt', ha = 'center', va = 'center')

            ax.text(x_pos, cs_y, 'CS', ha = 'center', va = 'center')
            ax.text(x_pos, ps_y, 'PS', ha = 'center', va = 'center')

    def plot_dwl(self, ax = None, annotate = True):
        """Plot deadweight loss region."""
        if ax == None:
            ax = plt.gca()

        market_p, market_q = self.demand.equilibrium(self.supply)
        p1, p2 = np.min(self.p), np.max(self.p)

        if self.tax > 0:
            ax.fill_between([self.q,market_q], y1 = (p2,market_p), y2 = (p1,market_p), 
                color = 'red', alpha = 0.1)

            if annotate:
                ax.text(  (2/3)*self.q +  (1/3)*market_q ,
                        np.mean(self.p), ' DWL', ha = 'center', va = 'center',
                        size = 8)

        elif self.subsidy > 0:
            ax.fill_between([market_q, self.q], y1 = (market_p,p2), y2 = (market_p,p1), 
                color = 'red', alpha = 0.1)

            if annotate:
                ax.text(  (2/3)*self.q +  (1/3)*market_q ,
                        np.mean(self.p), ' DWL', ha = 'center', va = 'center',
                        size = 8)
        
    def set_tax(self, tax):
        """Impose a per-unit tax. This overwrites other taxes or subsidies instead of adding to them.
        Nominal incidence is not considered, 
        so this works for taxes/subsidies imposed on either demand or supply."""
        
        self.tax = tax
        
        # Change in market quantity
        self.distortion = self.tax / (self.supply.slope - self.demand.slope)
        
        # update q relative to market quantity
        self.q = self.demand.equilibrium(self.supply)[1] - self.distortion
        
        # Update market prices
        self.p_consumer = self.demand.intercept + self.demand.slope * self.q
        self.p_producer = self.supply.intercept + self.supply.slope * self.q 
        if self.p_consumer != self.p_producer:
            self.p = self.p_consumer, self.p_producer
        else:
            self.p = self.p_consumer
        # don't allow negative quantities
        if self.q < 0:
            self.q = 0   
            
        # calculate DWL
        self.dwl = np.abs(self.distortion * self.tax * 0.5)
        
        # clear any subsidy
        self.subsidy = 0
        
    def set_subsidy(self, subsidy):
        """Impose a per-unit subsidy. This overwrites other taxes or subsidies instead of adding to them."""
        self.set_tax(-subsidy) # implement as negative tax
        self.subsidy = subsidy 
        self.distortion = -self.distortion
        self.tax = 0 # correct tax to zero
    
