import numpy as np
import matplotlib.pyplot as plt
from microecon.curves import Demand, Supply, intersection

class Equilibrium:
    
    def __init__ (self, demand: Demand, supply: Supply):
        """Equilibrium produced by demand and supply. Initialized as market equilibrium."""
        
        self.demand = demand
        self.supply = supply
        for dpiece in demand.pieces:
            for spiece in supply.pieces:
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

    def plot(self, ax=None):

        q_int = np.max([piece.q_intercept for piece in self.demand.pieces if piece])
        if ax is None:
            fig, ax = plt.subplots()

        # Plot eq pt
        x, y = self.q, self.p
        sty = {"lw":0.5, "ls": 'dotted', "color": 'gray'}
        ax.plot([x,x], [0,y], **sty)
        ax.plot([0,x], [y,y], **sty)
        ax.plot([x], [y], marker = '.', markersize=20)

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

        return ax

    def __repr__(self):
        s = f"Price: {self.p}\nQuantity: {self.q}"
        return s