
import numpy as np
import matplotlib.pyplot as plt

class Curve:

    def __init__ (self, intercept, slope, inverse = True):
        """Create curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P)."""

        if inverse:
            self.intercept = intercept
            self.slope = slope
            if slope != 0:
                self.q_intercept = -intercept/slope
            else:
                self.q_intercept = np.nan
            
        else:
            self.slope = 1/slope
            self.intercept = -intercept/slope
            if slope != 0:
                self.q_intercept = -self.intercept/self.slope
            else:
                self.q_intercept = np.nan
    
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
        if self.slope != 0:
            self.q_intercept = -self.intercept / self.slope
        
    def horizontal_shift(self, delta):
        """Shift curve horizontally by amount delta. Positive values are shifts to the right."""
        equiv_vert = delta * -self.slope
        self.intercept += equiv_vert  
        if self.slope != 0:
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
    

    def plot(self, ax = None, color = 'black', linewidth = 2, max_q = 10, clean = True):
        
        if ax == None:
            ax = plt.gca()

        # core plot
        q_ = self.q_intercept
        if np.isnan(q_): # if slope is 0
            q_ = 10 ** 10
        x2 = np.max([q_, max_q])
        y2 = self.intercept + self.slope * x2
        
        xs = np.linspace(0, x2,2)
        ys = np.linspace(self.intercept, y2, 2)
        
        ax.plot(xs, ys, color = color, linewidth = linewidth)

        if clean:
            ax.spines['left'].set_position('zero')
            ax.spines['bottom'].set_position('zero')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
    
    def equilibrium_plot(self, other_curve, ax = None, linewidth = 2, annotate = False, clean = True):
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

        if clean:
            self.equilibrium_plot_cleaner(other_curve)
  
        
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
        #min_int = np.min([self.q_intercept, other_curve.q_intercept])
        #max_int = np.max([self.q_intercept, other_curve.q_intercept])

        #min_x = np.min([-1, min_int])
        #max_x = np.max([0, max_int*1.1])
        #ax.set_xlim(min_x, max_x)

    def externality(self, externality, is_signed = True, is_positive = None):
        """Creates marginal social cost or benefit given a Curve and externality."""

        is_demand = self.slope < 0 # figure out if this is supply or demand curve

        if is_positive == True: # add to demand/MSB, substract from supply MSC
            if is_demand:
                externality = np.abs(externality)
            else:
                externality = - np.abs(externality)
        if is_positive == False:
            if is_demand:
                externality =  - np.abs(externality)
            else:
                externality = + np.abs(externality)


        social_curve = Curve(self.intercept + self.externalitiy, self.slope, inverse = True)
        return social_curve

        
class SocialBenefit:
    def __init__ (self, demand_array, *args):
        """Performs vertical summation of demand curves or Marginal Social Benefit curve.
        For public goods."""
        if (demand_array == None):
            demand_array = list(args)
        self.demand_array = demand_array
        
    def marginal_social_benefit(self, q):
        """Vertical summation of demand curves"""
        benefit = 0
        for curve in self.demand_array:
            benefit += np.max([0,curve.p(q)])
        return benefit
    
    def plot(self, ax = None, color = 'black', linewidth = 2, max_q = 10, clean = True):
        
        if ax == None:
            ax = plt.gca()

        intercepts = sorted([x.q_intercept for x in self.demand_array])
        slopes = sorted([x.slope for x in self.demand_array])
        
        max_x = intercepts[-1]

        x_vec = np.linspace(0,max_x, 1000)
        y_vec = [self.msb(x) for x in x_vec]

        ax.plot(x_vec, y_vec, color = color, linewidth = linewidth)

        if clean:
            # Make textbook-style plot window
            ax.spines['left'].set_position('zero')
            ax.spines['bottom'].set_position('zero')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        
    def efficient_outcome(self, other, quantity_guess = 1, tolerance = .05):
        """Find MSB and quantity with another aggregate or curve object. MSB as price does not give the
        corresponding quantity. """

        # MSB - MSC
        allocative_ineff = self.msb(quantity_guess) - other.productive_efficiency(quantity_guess)[1]

        has_cycled = False
        counter, last_counter = 0, 0
        scale = 1
        while np.abs(allocative_ineff) > tolerance:

            if allocative_ineff > 0: 
                # higher benefit than cost so increase quantity

                quantity_guess += tolerance * scale

                if counter > last_counter:
                    has_cycled = True
                    scale *= 0.5
                counter += 1
                last_counter = counter
            else: # must be strictly negative bc while condition
                # lower quantity
                quantity_guess -= tolerance
                counter += 1
            #print(price_guess, surplus)
            allocative_ineff = self.msb(quantity_guess) - other.productive_efficiency(quantity_guess)[1]
            
        return self.msb(quantity_guess), quantity_guess

    def private_outcome(self, mc_array):
        """Find private outcome. MC array must be ordered in alignment with demand_array."""

        # linear system of eq, solve for q1, qn
        # MB - MC = 0
        
        row_vecs, b_values = list(), list()
        n = len(mc_array) # number of agents
        for key, demand_cost in enumerate(zip(self.demand_array, mc_array)):
            demand = demand_cost[0]
            cost = demand_cost[1]

            cost_piece = np.concatenate([np.zeros(key), 
                    (-1 * cost.linear)*np.ones(1), np.zeros(n-key-1)])

            benefit_piece = demand.slope * np.ones(n)
            row_vec = cost_piece + benefit_piece
            b_value = cost.constant - demand.intercept

            row_vecs.append(row_vec)
            b_values.append(b_value)

        A = np.matrix(row_vecs)
        b = np.matrix(b_values).T

        #return A, b
        x = np.linalg.inv(A) * b
        x = x.squeeze()
        return x # q decisions

    def private_outcome_residual_demand_plots(self, mc_array, fig = None):
        """Plot demand residual demand."""

        q_vec = self.private_outcome(mc_array)
        q_vec = np.array(q_vec).squeeze()
        Q = q_vec.sum()

        if fig==None:
            fig = plt.gcf()

        n = len(mc_array)
        n_rows = n
        counter = 1
        for key, demand in enumerate(self.demand_array):

            supply = mc_array[key].supply()
            residual_Q = Q - q_vec[key] # q_{-i}

            demand.horizontal_shift(-residual_Q)

            ax = fig.add_subplot(n_rows,  2, counter)
            demand.equilibrium_plot(supply, ax = ax)
            ax.set_xlabel("Private Contribution")
            ax.set_title("Residual Demand and Private Production")
            xlim_max = ax.get_xlim()[1]
            ax.set_xlim(0, xlim_max)
            ylim_max = ax.get_ylim()[1]
            ax.set_ylim(0, ylim_max)

            sharex = None
            if key > 0:
                sharex = ax2 # previous plot above
            ax2 = fig.add_subplot(n_rows, 2, counter + 1, sharey = ax, sharex = sharex)
            demand.horizontal_shift(residual_Q) # shift back
            demand.plot(ax = ax2)
            ax2.plot([Q,Q], [0, demand.p(Q)], linestyle = 'dashed')
            ax2.set_xlabel("Public Provision")
            ax2.set_title("Demand and Total Consumption")

            counter += 2


        plt.tight_layout()

        
    def msb(self,q):
        """Abbreviation method for marginal_social_benefit()."""
        return self.marginal_social_benefit(q)


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

    def productive_efficiency(self, Q):
        """Find q1, ..., qn and p at total quantity Q."""

        #distributive/productive efficiency requires MB = MB or MC = MC
        n = len(self.curve_array)
        
        # set up linear system to solve for q1, ..., qn, and MC.
        # q1 + q2 + ... + qn + 0*MC = Q
        # mc1 = MC
        # mc2 = MC 

        accounting = np.concatenate([np.ones(n), np.array([0])])

        #
        b_vec = np.array([0]+[])
        from itertools import combinations

        row_vectors = [accounting]
        b_values = [ Q]
        for key, curve in enumerate((self.curve_array)):

            # 0 + slope*q_curve + 0 - MC =  - curve.intercept
            c_vec = np.concatenate([np.zeros(key), 
                        curve.slope*np.ones(1), np.zeros(n-key-1), -1*np.ones(1)])

            row_vectors.append(c_vec)
            b_values.append(-curve.intercept)

        A = np.matrix(row_vectors)
        b = np.matrix(b_values).T

        #return A, b
        x = np.linalg.inv(A) * b
        x = x.squeeze()
        return x[0,:-1], x[0,-1] # q1 ... qn, MC

        # all 
        #total_p = 0
        #for curve in self.curve_array:
        #    total_p += np.max([0,curve.p(q)])
        #return total_p

    def distributive_efficiency(self, Q):
        return self.productive_efficiency(Q)

    def plot(self, ax = None, color = 'black', linewidth = 2, max_q = 10, clean = True):
        
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
            y_vec = np.linspace(0,np.max([10,max_y*2]), 1000)
            x_vec = [self.q(y) for y in y_vec]

            ax.plot(x_vec, y_vec, color = color, linewidth = linewidth)
        if clean:
            self.plot_clean()

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

        if type(other) == Aggregate:
       
            kink_list = self.kinks() + other.kinks()
        else:
            kink_list = self.kinks()

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

    def __init__ (self , intercept , slope , inverse = True):
        """Create supply curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P).""" 
        Curve.__init__(self, intercept, slope, inverse)
  
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
        
    def plot_old(self, ax = None, annotate = False, clean = True, fresh_ticks = True):
        """deprecated"""
        if ax == None:
            ax = plt.gca()
        if self.p_producer == self.p_consumer:
            self.demand.equilibrium_plot(self.supply, ax = ax, annotate = annotate)
        else:
            pass
        
        if clean:
            self.plot_clean(ax, fresh_ticks = fresh_ticks)
            
    def plot(self, ax = None, annotate = False, clean = True, fresh_ticks = True):
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
        """Clean Equilibrium plot."""
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
            ax.set_xticks([x for x in important_x if not np.isnan(x)])
            ax.set_yticks([x for x in important_y if not np.isnan(x)])
        else:
            ax.set_xticks(sorted(list([x for x in combined_xticks if not np.isnan(x)])))
            ax.set_yticks(sorted(list([x for x in combined_yticks if not np.isnan(x)])))

        # label demand and supply curves
        # not written yet

        # set limits
        x_int = self.demand.q_intercept*1.04
        if np.isnan(x_int):
            x_int = 2*self.q

        ax.set_xlim(0, x_int)
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
        
    def plot_surplus(self, ax = None, annotate = True, items = ['cs', 'ps', 'govt']):
        
        if ax == None:
            ax = plt.gca()

        items = [x.lower() for x in items] 
        
        p,q = self.p, self.q
        
        # CS region
        if 'cs' in items:
            cs_plot = ax.fill_between([0,q], y1 = [self.demand.intercept, self.p_consumer], 
            y2 = self.p_consumer, 
            alpha = 0.1)
        
        # fix later for negative 
        if 'ps' in items:
            ps_plot = ax.fill_between([0,q], y1 = [self.supply.intercept, self.p_producer], 
            y2 = self.p_producer, 
            color = 'C1', alpha = 0.1)
        
        if type(self.p) == tuple:
            if 'govt' in items:
                high_price, low_price = np.max(p), np.min(p)
                g_plot = ax.fill_between([0,q], y1 = high_price, y2 = low_price,
                    color = 'C2', alpha = 0.1)

        if annotate:
            x_pos = self.q/3

            # meean between price and along supply curve
            ps_y = np.mean([self.p_producer, self.supply.intercept + self.supply.slope * x_pos])
            cs_y = np.mean([self.p_consumer, self.demand.intercept + self.demand.slope * x_pos])
            govt_y = np.mean(p)

            if type(self.p) == tuple:
                if 'govt' in items:
                    ax.text(self.q/4, govt_y, 'Govt', ha = 'center', va = 'center')

            if 'cs' in items:
                ax.text(x_pos, cs_y, 'CS', ha = 'center', va = 'center')
            if 'ps' in items:
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



### COSTS 

class Cost:

    def __init__ (self, constant, linear, quadratic,  currency = "$", reciprocal = 0):
        """Create a quadratic cost curve,
        constant + linear*q + quadratic*q^2. Reciprocal just for average costs"""

        self.constant = constant
        self.linear = linear
        self.quadratic = quadratic
        self.currency = currency
        self.reciprocal = reciprocal

    def cost(self, q):
        """Return cost at quantity q."""
        if self.reciprocal == 0: # allows for q = 0 calcs
            return self.constant + self.linear * q + self.quadratic * (q**2)
        return self.constant + self.linear * q + self.quadratic * (q**2) + self.reciprocal * (1/q)

    def variable_cost(self):
        """Return Cost object less fixed costs."""
        return Cost(constant = 0, linear = self.linear, quadratic = self.quadratic, currency = self.currency)

    def marginal_cost(self):
        """Finds marginal cost, assuming cost is quadratic."""
        return MarginalCost(constant = self.linear, linear = 2*self.quadratic, quadratic = 0, currency = self.currency)

    def average_cost(self):
        return Cost(constant = self.linear, linear = self.quadratic, quadratic = 0, reciprocal = self.constant, currency = self.currency)


    def efficient_scale(self):
        """Find q that minimizes average cost."""

        # Avg Cost = constant/q + linear + quadratic * q
        # d/dq Avg Cost = - constant/q**2 + quadratic = 0
        # q**2 = constant / quadratic

        return np.sqrt(self.constant/self.quadratic)

    def breakeven_price(self):
        """Assume perfect competition and find price such that economic profit is zero."""

        # find MC = ATC
        return self.marginal_cost().cost(self.efficient_scale()) 

    def shutdown_price(self):
        """Assume perfect competition and find price such that total revenue = total variable cost."""

        var = self.variable_cost()
        return var.marginal_cost().cost(var.efficient_scale())

    def plot(self, ax = None, max_q = 100, label = None, min_plotted_q = 0.1):
        """Plot the cost curve. 
        min_plotted_q is used when the cost goes to infinity as q->0 to keep y-limits from also going to infinity."""
        if ax == None:
            ax = plt.gca()

        x_vals = np.linspace(0, max_q, max_q*5 + 1)
        if self.reciprocal != 0:
            x_vals = x_vals[x_vals >= min_plotted_q]
        y_vals = [self.cost(q) for q in x_vals]

        ax.plot(x_vals, y_vals, label = label)
        ax.set_xlabel("Quantity")
        ax.set_ylabel("Cost ({})".format(self.currency))


        # Make textbook-style plot window
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)



class TotalCost(Cost):
    """Creates linear, downward-sloping demand curve."""

    def __init__ (self , constant, linear, quadratic):
        """Create demand curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P).""" 
        Cost.__init__(self, constant, linear, quadratic)

    def long_run_plot(self, ax = None):

        ac = self.average_cost()
        mc = self.marginal_cost()

        if ax == None:
            ax = plt.gca()


        # find price and q
        p, q = self.breakeven_price(), self.efficient_scale()

        max_q = int(2*q)
        ac.plot(ax, label = 'LRAC', max_q = max_q)
        mc.plot(ax, label = "MC", max_q = max_q)

        ax.plot([0,q], [p,p], linestyle = 'dashed', color = 'gray')
        ax.plot([q,q], [0,p], linestyle = 'dashed', color = 'gray')
        ax.plot([q], [p], marker = 'o')
        ax.set_xlim(0,max_q)
        ax.legend()

    def cost_profit_plot(self, p, ax = None, items = ['tc', 'tr', 'profit']):
        if ax == None:
            ax = plt.gca()

        items = [str(x).lower() for x in items]

        # set p = mc
        mc = self.marginal_cost()
        q = mc.q(p)

        # plot AC and MC 
        self.average_cost().plot(label = "ATC")
        mc.plot(label = "MC")


        # plot price and quantity
        ax.plot([0,q], [p,p], linestyle = 'dashed', color = 'gray')
        ax.plot([q,q], [0,p], linestyle = 'dashed', color = 'gray')
        ax.plot([q], [p], marker = 'o')


        atc_of_q = self.average_cost().cost(q)

        if 'profit' in items:
            # profit 
            profit = q * (p - atc_of_q)
            if profit > 0:
                col = 'green'
            else:
                col = 'red'
            ax.fill_between([0,q], atc_of_q, p, color = col, alpha = 0.3, label = r"$\pi$", hatch = "\\")

        if 'tc' in items:
            # total cost
            ax.fill_between([0,q], 0, atc_of_q, facecolor = 'yellow', alpha = 0.1, label = 'TC', hatch = "/")

        if 'tr' in items:
            ax.fill_between([0,q], 0, p, facecolor = 'blue', alpha = 0.1, label = 'TR', hatch = '+')



        ax.set_ylim(0,p*1.5)
        ax.set_xlim(0,q*1.5)
        ax.legend()






        
class MarginalCost(Cost):

    def __init__ (self , constant, linear, quadratic = 0 , currency = '$'):
        """Create demand curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P).""" 
        Cost.__init__(self, constant, linear, quadratic, currency)
        
    def q(self, p):

        #p = self.constant + self.linear * q + self.quadratic * q**2
        # self.quadratic * q**2 + self.linear * q + self.constant - p
        roots = np.roots([self.quadratic, self.linear, self.constant - p])

        if self.quadratic != 0:
            print('No quadratic MC please.')

        root = roots[0]

        return root

    def supply(self):
        """Convert to a supply object"""
        return Supply(intercept = self.constant, slope = self.linear)


class LongRunCompetitiveEquilibrium:
    def __init__ (self, demand, total_cost):
        """Create long-run equilibrium for perfectly comepetitive market with identical firms."""
        self.total_cost = total_cost
        self.demand = demand

        self.p = self.total_cost.breakeven_price()
        self.firm_q = self.total_cost.efficient_scale()

        self.market_q = self.demand.q(self.p)
        self.n_firms = self.market_q / self.firm_q

    def plot(self, fig = None):

        #fig, ax = plt.subplots(1,2, sharey = True)
        if fig == None:
            fig = plt.gcf()

        firm_ax = fig.add_subplot(1, 2 ,1)

        self.total_cost.long_run_plot(firm_ax)
        firm_ax.set_title('Firm')

        mkt_ax = fig.add_subplot(1, 2 ,2, sharey = firm_ax)

        supply_curve = Supply(self.p, 0)
        market_eq = Equilibrium(self.demand, supply_curve)

        market_eq.plot(mkt_ax)
        mkt_ax.set_title("Market")

        firm_ax.set_xlabel("Firm Quantity")
        mkt_ax.set_xlabel("Market Quantity")


class Game:
    def __init__ (self, u00, u01, u10, u11, utility_profiles = True,
        player_names = ['Player A', 'Player B'],
        A_action_names = ['action 0', 'action 1'],
        B_action_names = ['action 0', 'action 1']):
        """Two player game with actions 0 or 1 for each player.
        Enter payoffs for players A (row player, index 0) and B (column player, index 1)
        depending on action profiles. 
        uij: (utility to A, utility to B) if A takes action j and B takes action j
        
        Use utility_profile = False to instead have interpretation
        uij = (utility to Player i if i takes action J and -i takes 0, 
                    utility to Player i if i takes action J and -i takes 1)
        """
    
        
        if utility_profiles:
            # each pair represents payoffs to each player given an outcome
            self.payoffs00 = u00
            self.payoffs01 = u01
            self.payoffs10 = u10
            self.payoffs11 = u11
            
        else:
            # each pair represents possible payoff ot player given their action 
            self.Au0 = u00
            self.Au1 = u01
            self.Bu0 = u10
            self.Bu1 = u11

            self.payoffs00 = self.Au0[0], self.Bu0[0]
            self.payoffs01 = self.Au0[1], self.Bu1[0]
            self.payoffs10 = self.Au1[0], self.Bu0[1]
            self.payoffs11 = self.Au1[1], self.Bu1[1]
        
        
            
    def best_response(self, action_profile):
        """If multiple, this chooses the action already specified."""
        
        action_profile = str(action_profile[0]) + str(action_profile[1])
        payoffs = self.__dict__['payoffs'+action_profile]

        profile_list = list(action_profile) # convert for mutability
        
        br_profile = list()
        for player in [0,1]:
            action = action_profile[player]                
            deviation = 1 - int(action)

            profile_list = list(action_profile) # convert for mutability
            profile_list[player] = str(deviation)

            deviation_profile =  ''.join(profile_list)

            dev_payoffs = self.__dict__['payoffs'+deviation_profile]

            if dev_payoffs[player] > payoffs[player]:
                br = deviation
            else:
                br = action
            br_profile.append(br)
            
        return br_profile
    
    def nash(self):
        """Returns a set pure strategy nash equilibria."""
        
        equilibria = set()
        for action_profile in ['00', '01', '10', '11']:
            
            payoffs = self.__dict__['payoffs'+action_profile]
            
            is_equilibrium = True
            # consider deviations
            profile_list = list(action_profile) # convert for mutability
            for player in [0,1]: ### Simplify this with new best response method
                action = action_profile[player]                
                deviation = 1 - int(action)
        
                profile_list = list(action_profile) # convert for mutability
                profile_list[player] = str(deviation)
        
                deviation_profile =  ''.join(profile_list)
            
                dev_payoffs = self.__dict__['payoffs'+deviation_profile]
                
                if dev_payoffs[player] > payoffs[player]:
                    
                    is_equilibrium = False
                    
            # did equilibria survive
        
            
            if is_equilibrium:
                
                # rename
                renamed = ''
                for action, player in zip(action_profile, 'AB'):
                    new = player + action
                    renamed += new
                
                equilibria.add(renamed)
                
        return equilibria
                
    def table(self, ax = None, show_solution = True):
        
        if ax == None:
            ax = plt.gca()
            
        for point in ['00', '01', '10', '11']:
            
            # point is an aciton profile
            br = self.best_response(point)
            
            A_is_br = br[0] == point[0]
            B_is_br = br[1] == point[1]
            
            xy = - int(point[0]), int(point[1])
            
            index = 1
            
            location = xy[1], xy[0]
            
            rec = plt.Rectangle(location, width = -1, height = -1, facecolor = 'white', 
                                edgecolor = 'black',
                               linewidth= 2)
            ax.add_artist(rec)
            
            payoff = self.__dict__['payoffs'+point]
            sA, sB = str(payoff[0]),  str(payoff[1])
            bbox = None
            if show_solution:
                plt.rc('text', usetex=True)
                if A_is_br:
                    sA = r"\underline{" + str(payoff[0]) + r"}"
                if B_is_br:
                    sB = r"\underline{" + str(payoff[1]) + r"}"
                if A_is_br and B_is_br:
                    bbox = dict(facecolor = 'lightyellow',
                            edgecolor = 'black', alpha = 0.85)
                
            s = sA + ", " + sB
            ax.text(xy[1] - 0.5 , xy[0] - 0.5, s, va = 'center', ha = 'center',
                   size = 31, bbox = bbox) #, font = 'Courier New')
            
        ax.set_aspect('equal')
        ax.set_ylim(-2.05,0.05)
        ax.set_xlim(-1.05,1.05)
        
        # Label players and actions
        ax.text(-0.08, 0.5, "Player A", rotation = 90,
               transform = ax.transAxes, 
                ha = 'right', 
                va = 'center',
                size = 20)
        
        ax.text(0, 0.25, "action 1", rotation = 90,
               transform = ax.transAxes, 
                ha = 'right', 
                va = 'center',
                size = 12)
        
        ax.text(0, 0.75, "action 0", rotation = 90,
               transform = ax.transAxes, 
                ha = 'right', 
                va = 'center',
                size = 12)
        
        ax.text(0.5, 1.08, "Player B", rotation = 0,
               transform = ax.transAxes, 
                ha = 'center', 
                va = 'bottom',
                size = 20)
        
        ax.text(0.75, 1, "action 1", rotation = 0,
               transform = ax.transAxes, 
                ha = 'center', 
                va = 'bottom',
                size = 12)
        
        ax.text(0.25, 1, "action 0", rotation = 0,
               transform = ax.transAxes, 
                ha = 'center', 
                va = 'bottom',
                size = 12)
        
        ax.axis('off')
                    

        
    def weakly_dominant_strategies(self, players = ['A','B']):
        
        players = [x.lower() for x in players]
        
        a_doms = set()
        b_doms = set()
        
        if 'a' in players:
            
            # does 0 dominate 1
            
            dominates0 = (self.payoffs00[0] >= self.payoffs10[0]) and (self.payoffs01[0] >= self.payoffs11[0])
            dominates1 = (self.payoffs00[0] <= self.payoffs10[0]) and (self.payoffs01[0] <= self.payoffs11[0])
            
            if dominates0:
                a_doms.add(0)
            if dominates1:
                a_doms.add(1)
           
        if 'b' in players:
            
            # does 0 dominate 1
            
            dominates0 = (self.payoffs00[1] >= self.payoffs01[1]) and (self.payoffs10[1] >= self.payoffs11[1])
            dominates1 = (self.payoffs00[1] <= self.payoffs01[1]) and (self.payoffs10[1] <= self.payoffs11[1])
            
            if dominates0:
                b_doms.add(0)
            if dominates1:
                b_doms.add(1)
        
        
        
        return {'A': a_doms, "B": b_doms}
        
