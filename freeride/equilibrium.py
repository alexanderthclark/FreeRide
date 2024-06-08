import numpy as np
import matplotlib.pyplot as plt
from freeride.curves import Demand, Supply, intersection
from freeride.plotting import AREA_FILLS

class Equilibrium:
    
    def __init__ (self, demand: Demand, supply: Supply, tax=0):
        """Equilibrium produced by demand and supply. Initialized as market equilibrium."""
        
        self.demand = demand
        self.supply = supply
        self.__tax = tax
        self._compute(tax)

    def _compute(self, tax=None):
        if tax is None:
            tax = self.__tax

        # shift demand as if statuatory incidence is on consumers
        demand = self.demand
        if tax:
            tax_demand_elements = [d.vertical_shift(-tax, inplace=False) for d in demand.elements if d]
            demand = Demand(elements=tax_demand_elements)

        for dpiece in demand.pieces:
            for spiece in self.supply.pieces:
                if dpiece and spiece:
                    s_domain = spiece._domain
                    d_domain = dpiece._domain
                    p, q = intersection(dpiece, spiece)
                    in_demand = d_domain[1] <= q <= d_domain[0]
                    in_supply = s_domain[0] <= q <= s_domain[1]
                    if in_demand and in_supply:
                        self.q = q
                        self.p = p
                        break

        self.__p_consumer = self.p + self.__tax
        self.__p_producer = self.p

        # Two prices if there is a tax or subsidy
        if self.__tax:
            self.p = self.__p_consumer, self.__p_producer

        return q, p

    def plot(self, ax=None, surplus=False):

        q_int = np.max([piece.q_intercept for piece in self.demand.pieces if piece])
        if ax is None:
            fig, ax = plt.subplots()

        # Plot eq pt
        x, y = self.q, self.__p_consumer
        sty = {"lw":0.5, "ls": 'dotted', "color": 'gray'}
        ax.plot([x,x], [0,y], **sty)
        ax.plot([0,x], [y,y], **sty)
        ax.plot([x], [y], marker = '.', markersize=14, color='black')

        if self.__tax:
            y = self.__p_producer
            ax.plot([x,x], [0,y], **sty)
            ax.plot([0,x], [y,y], **sty)
            ax.plot([x], [y], marker = '.', markersize=14, color='black')

        # Plot curves and mark important ticks
        self.demand.plot(ax=ax)
        xticks0, yticks0 = set(ax.get_xticks()), set(ax.get_yticks())
        self.supply.plot(ax=ax, max_q=q_int)
        xticks1, yticks1 = set(ax.get_xticks()), set(ax.get_yticks())
        xticks = xticks0.union(xticks1)
        xticks.add(x)
        yticks = yticks0.union(yticks1)
        yticks.add(y)
        ax.set_xticks(list(xticks))
        ax.set_yticks(list(yticks))

        if surplus:
            #self.demand.plot_surplus(p=self.__p_consumer, ax=ax)
            #self.supply.plot_surplus(p=self.__p_producer, ax=ax)
            self.plot_surplus(ax=ax)

        return ax

    def plot_surplus(self, ax):

        self.demand.plot_surplus(p=self.__p_consumer, ax=ax)
        self.supply.plot_surplus(p=self.__p_producer, ax=ax)

        # add deadweight loss and govt revenue
        if self.__tax > 0:
            e_star = Equilibrium(demand=self.demand, supply=self.supply)
            q_star, p_star = e_star.q, e_star.p
            q = self.q
            red = (1, 0.5, 0.5)
            for piece in self.demand.pieces + self.supply.pieces:
                if piece:
                    minq, maxq = np.min(piece._domain), np.max(piece._domain)

                    irrelevant = (q > maxq) or (q_star < minq)
                    relevant = not irrelevant
                    dropped = relevant and (q < minq)
                    partial = relevant and (minq < q < maxq)

                    if dropped:
                        piece.plot_area(p=p_star, color=red, ax=ax)
                    elif partial:
                        piece.plot_area(p=p_star, q=[q, maxq], color=red, ax=ax)

            # Govt revenue
            ax.fill_between([0, self.q], self.__p_consumer, 
                self.__p_producer,
                color = .93*np.ones(3))
        
        if self.__tax < 0:
            e_star = Equilibrium(demand=self.demand, supply=self.supply)
            q_star, p_star = e_star.q, e_star.p
            q = self.q
            red = (1, 0.5, 0.5)
            for piece in self.demand.pieces + self.supply.pieces:
                if piece:
                    minq, maxq = np.min(piece._domain), np.max(piece._domain)

                    irrelevant = (q < minq) or (q_star > maxq)
                    relevant = not irrelevant
                    case_a = relevant and (minq < q_star < q < maxq)
                    #partial = relevant and (minq < q < maxq)

                    if case_a:
                        piece.plot_area(p=p_star, q = [q_star, q], color=red, ax=ax)
                    elif relevant:
                        piece.plot_area(p=p_star, q=[minq, np.min([q, maxq])], color=red, ax=ax)

    @property
    def consumer_surplus(self):
        return self.demand.consumer_surplus(self.__p_consumer)

    @property
    def producer_surplus(self):
        #broken
        return self.supply.producer_surplus(self.__p_producer)

    @property
    def govt_revenue(self):
        return self.__tax * self.q

    @property    
    def total_surplus(self):
        return self.producer_surplus + self.consumer_surplus + self.govt_revenue

    def __repr__(self):
        s = f"Price: {self.p}\nQuantity: {self.q}"
        return s

    @property
    def tax(self):
        return self.__tax

    @tax.setter
    def tax(self, new_value):
        self.__tax = new_value
        self._compute()

    @property
    def p_consumer(self):
        return self.__p_consumer

    @property
    def p_producer(self):
        return self.__p_producer
    
    @classmethod
    def _recompute(cls, self, tax):

        new_demand_elements = [d.vertical_shift(-tax, inplace=False) for d in self.demand.elements if d]
        new_demand = Demand(elements=new_demand_elements)

        e = cls(demand=new_demand, supply=self.supply)
        e.__tax = tax
        e.__p_consumer = e.p + tax
        e.__p_producer = e.p
        return e

