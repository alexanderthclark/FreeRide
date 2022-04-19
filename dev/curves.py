import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import abc
import numbers




############################################################
#### Plot Helpers
plotprops = {'color': 'black', 'linewidth': 2}

def textbook_axes(ax = None):
    if ax == None:
        ax = plt.gca()
    
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

############################################################
#### Curve Classes


class PolyBase(np.polynomial.Polynomial):
    
    def __init__(self, coef):
        super().__init__(coef)
        
    def p(self, q: float):
        "Price given a value q"
        return self.__call__(q)
    
    def q(self, p):
        "Quantity given a value p"
        
        coef2 = (self.coef[0]-p, *self.coef[1:])[::-1]
        roots = np.roots(coef2)
        
        if roots.shape == (1,):
            return roots[0]
        else:
            return roots

    def plot(self, ax = None, max_q = 100, label = None, min_plotted_q = 0):
        """Plot the cost curve. 
        min_plotted_q is used when the cost goes to infinity as q->0 to keep y-limits from also going to infinity."""
        if ax == None:
            ax = plt.gca()

        x_vals = np.linspace(0, max_q, max_q*5 + 1)
        #if self.reciprocal != 0:
        x_vals = x_vals[x_vals >= min_plotted_q]
        y_vals = self(x_vals)

        ax.plot(x_vals, y_vals, label = label)
        #ax.set_xlabel("Quantity")
        #ax.set_ylabel("Cost ({})".format(self.currency))


        # Make textbook-style plot window
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    def _repr_latex_(self):
        
        # overwrite ABCPolyBase Method to use p/q instead of x\mapsto
        # get the scaled argument string to the basis functions
        off, scale = self.mapparms()
        if off == 0 and scale == 1:
            term = 'q'
            needs_parens = False
        elif scale == 1:
            term = f"{self._repr_latex_scalar(off)} + q"
            needs_parens = True
        elif off == 0:
            term = f"{self._repr_latex_scalar(scale)}q"
            needs_parens = True
        else:
            term = (
                f"{self._repr_latex_scalar(off)} + "
                f"{self._repr_latex_scalar(scale)}q"
            )
            needs_parens = True

        mute = r"\color{{LightGray}}{{{}}}".format

        parts = []
        for i, c in enumerate(self.coef):
            # prevent duplication of + and - signs
            if i == 0:
                coef_str = f"{self._repr_latex_scalar(c)}"
            elif not isinstance(c, numbers.Real):
                coef_str = f" + ({self._repr_latex_scalar(c)})"
            elif not np.signbit(c):
                coef_str = f" + {self._repr_latex_scalar(c)}"
            else:
                coef_str = f" - {self._repr_latex_scalar(-c)}"

            # produce the string for the term
            term_str = self._repr_latex_term(i, term, needs_parens)
            if term_str == '1':
                part = coef_str
            else:
                part = rf"{coef_str}\,{term_str}"

            if c == 0:
                part = mute(part)

            parts.append(part)

        if parts:
            body = ''.join(parts)
        else:
            # in case somehow there are no coefficients at all
            body = '0'

        return rf"$p = {body}$"
        
############################################################
#### Demand/Supply Classes


class Affine(PolyBase):
    
    def __init__(self, intercept, slope, inverse = True):
        
        if not inverse:
            slope, intercept = 1/slope, -intercept/slope
        
        coef = (intercept, slope)
        super().__init__(coef)
        self.intercept = intercept
        self.slope = slope
        
        if slope != 0:
            self.q_intercept = -intercept/slope
        else:
            self.q_intercept = np.nan
                
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
            
    def price_elasticity(self, p):
        "Point price elasticity at price p"
        
        if p < 0:
            raise ValueError('Negative price.')
        if p > self.intercept:
            raise ValueError("Price above choke price.")
        
        q = self.q(p)
        e = (1/self.slope) * (p/q)
        return e
    
    def midpoint_elasticity(self, p1, p2):
        """Find price elasticity between two prices, using the midpoint formula. """
        
        if (p1 < 0) or (p2 < 0):
            raise ValueError('Negative price.')
        if (p1 > self.intercept) or (p2 > self.intercept):
            raise ValueError("Price above choke price.")
        
        mean_p = 0.5*p1 + 0.5*p2
        return self.price_elasticity(mean_p)
  

    def plot(self, ax = None, textbook_style = True, max_q = 10, 
             color = 'black', linewidth = 2, label = True):
        
        if ax == None:
            ax = plt.gca()

        # core plot
        q_ = self.q_intercept
        if np.isnan(q_): # if slope is 0
            q_ = 10 ** 10
        if type(self).__name__ == "Supply":
            x2 = np.max([max_q, q_*2])
        else:
            x2 = q_
        
        y2 = self(x2)
        
        xs = np.linspace(0, x2,2)
        ys = np.linspace(self.intercept, y2, 2)
        #ys = np.maximum(self.p(xs), 0)
        ax.plot(xs, ys, color = color, linewidth = linewidth)

        if textbook_style:
            textbook_axes(ax)
            
        if label == True:
            
            # Label Curves
            if type(self).__name__ == 'Demand':
                x0 = self.q_intercept * .95
            else:
                x0 = ax.get_xlim()[1] * .9
            
            y_delta = (ax.get_ylim()[1] - ax.get_ylim()[0])/30
            y0 = self.p(x0) + y_delta
            ax.text(x0, y0, type(self).__name__[0], va = 'bottom', ha = 'center', size = 14)

            # Label Axes
            ax.set_ylabel("Price")
            ax.set_xlabel("Quantity")

        # fix lims
        ylims = ax.get_ylim()
        ax.set_ylim(0, ylims[1])
        
class PerfectlyElastic:
    pass
class PerfectlyInelastic:
    pass
        
class Demand(Affine):
    
    def __init__(self, intercept, slope, inverse = True):
        
        super().__init__(intercept, slope, inverse)
        
        if self.slope > 0:
            raise ValueError("Upward sloping demand curve.")
    
    def consumer_surplus(self, p):
        """Calculates consumer surplus at a price p."""
        q = np.max([0, self.q(p)])
        return (self.p(0) - p) * q * 0.5
                
        
    def plot_surplus(self, p, ax = None):
        """Plot consumer surplus."""
        
        if ax == None:
            ax = plt.gca()
            
        if p <= self.intercept:
            cs_plot = ax.fill_between([0, self.q(p)], y1 = [self.intercept, p], y2 = p,  alpha = 0.1)
        
class Supply(Affine):
    
    def __init__(self, intercept, slope, inverse = True):
        
        super().__init__(intercept, slope, inverse)
        
        if self.slope < 0:
            raise ValueError("Downward sloping demand curve.")
            
            
    def producer_surplus(self, p):
        """Calculates producer surplus at a price, disallowing negative costs/WTS."""
        if p <= self.p(0):
            return 0
        
        q = self.q(p)
        

        if self.q_intercept > 0:
            rectangle_width = np.min([q,self.q_intercept])
            rectangle_area = rectangle_width * p
            triangle_area = np.max([q - self.q_intercept]) * p * 0.5
            return rectangle_area + triangle_area
        
        return (p - self.p(0)) * q * 0.5

    
    def plot_surplus(self, p, ax = None):
        
        if p < 0:
            raise ValueError("Negative price.")
        
        if ax == None:
            ax = plt.gca()
        q = self.q(p)
        # fix later for negative 
        
        if q <= 0:
            return None
        
        qq = np.min([q, self.q_intercept])

        if q > self.q_intercept > 0:            
      
            rectangle_plot = ax.fill_between([0, qq, q], y1 = [0,0,p], y2 = p, color = 'C1', alpha = 0.1)
            
        elif self.q_intercept >= q > 0:
            rectangle_plot = ax.fill_between([0,q], y1 = 0, y2 = p, color = 'C1', alpha = 0.1)

        else:
            ps_plot = ax.fill_between([0,q], y1 = [self.intercept, p], y2 = p, color = 'C1', alpha = 0.1)
        
            
############################################################
#### Cost Classes

class Cost(PolyBase):
    """Polynomial cost curve"""

    def __init__(self, *coef):

        # if there's an array just use the array
        if type(coef[0]) not in [float, int]:
    
            if len(coef) > 1:
                raise ValueError("Pass a single array or all multiple scalars.")

            coef = coef[0]
        super().__init__(coef)

        self.coef = coef
    
    def _repr_latex_(self):
        
        # overwrite ABCPolyBase Method to use p/q instead of x\mapsto
        # get the scaled argument string to the basis functions
        off, scale = self.mapparms()
        if off == 0 and scale == 1:
            term = 'q'
            needs_parens = False
        elif scale == 1:
            term = f"{self._repr_latex_scalar(off)} + q"
            needs_parens = True
        elif off == 0:
            term = f"{self._repr_latex_scalar(scale)}q"
            needs_parens = True
        else:
            term = (
                f"{self._repr_latex_scalar(off)} + "
                f"{self._repr_latex_scalar(scale)}q"
            )
            needs_parens = True

        mute = r"\color{{LightGray}}{{{}}}".format

        parts = []
        for i, c in enumerate(self.coef):
            # prevent duplication of + and - signs
            if i == 0:
                coef_str = f"{self._repr_latex_scalar(c)}"
            elif not isinstance(c, numbers.Real):
                coef_str = f" + ({self._repr_latex_scalar(c)})"
            elif not np.signbit(c):
                coef_str = f" + {self._repr_latex_scalar(c)}"
            else:
                coef_str = f" - {self._repr_latex_scalar(-c)}"

            # produce the string for the term
            term_str = self._repr_latex_term(i, term, needs_parens)
            if term_str == '1':
                part = coef_str
            else:
                part = rf"{coef_str}\,{term_str}"

            if c == 0:
                part = mute(part)

            parts.append(part)

        if parts:
            body = ''.join(parts)
        else:
            # in case somehow there are no coefficients at all
            body = '0'

        return rf"$q \mapsto {body}$"


    def cost(self, q):
        return self(q)

    def variable_cost(self):
        """Remove constant term in polynomial."""
        new_coef = 0, *self.coef[1:]
        return Cost(new_coef)

    def marginal_cost(self):
        new_coef = [(key+1)*c for key,c in enumerate(self.coef[1:])]
        return Cost(new_coef)

    def average_cost(self):
        #new_coef = [c for c in self.coef[1:]]
        return AverageCost(self.coef)



    def efficient_scale(self):
        """Find q that minimizes average cost."""

        # Avg Cost = constant/q + linear + quadratic * q
        # d/dq Avg Cost = - constant/q**2 + quadratic = 0
        # q**2 = constant / quadratic
        coef = self.coef
        try:
            constant = coef[0]
            quad = coef[2]

            return np.sqrt(constant/quad)

        except IndexError:
            
            "increasing returns to scale forever"
            if constant > 0:
                return np.inf

            elif len(coef) <= 2: # linear costs
                raise ValueError('constant returns to scale')


    def breakeven_price(self):
        """Assume perfect competition and find price such that economic profit is zero."""

        # find MC = ATC
        return self.marginal_cost().cost(self.efficient_scale()) 

    def shutdown_price(self):
        """Assume perfect competition and find price such that total revenue = total variable cost."""

        var = self.variable_cost()
        return var.marginal_cost().cost(var.efficient_scale())



    def long_run_plot(self, ax = None):
        ac = self.average_cost()
        mc = self.marginal_cost()

        if ax == None:
            ax = plt.gca()

        p, q = self.breakeven_price(), self.efficient_scale()

        if q == np.inf:

            return 'in prog'

        max_q = int(2*q)
        #ac.plot(ax, label = 'LRAC', max_q = max_q)
        ax_q = np.linspace(0, max_q, 1000)
        ax_p = ac(ax_q)
        ax.plot(ax_q, ax_p, label = 'LRAC')
        mc.plot(ax, label = "MC", max_q = max_q)

        ax.plot([0,q], [p,p], linestyle = 'dashed', color = 'gray')
        ax.plot([q,q], [0,p], linestyle = 'dashed', color = 'gray')
        ax.plot([q], [p], marker = 'o')
        ax.set_xlim(0,max_q)
        ax.set_ylim(0,2*p)
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


        atc_of_q = self.average_cost()(q)

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




class AverageCost:

    def __init__(self , coef):
        
        self.poly_coef = coef[1:]
        self.coef = coef

    def __call__(self, q):
        return Cost(self.coef)(q) / q

    def cost(self, q):
        return self(q)

    def plot(self, ax = None, max_q = 10):
        
        if ax == None:
            ax = plt.gca()

        xs = np.linspace(0.01, max_q, int(10*max_q))
        ys = self(xs)
        ax.plot(xs, ys, label = label)
