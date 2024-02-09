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

        self.demand.plot(ax=ax)
        self.supply.plot(ax=ax, max_q=q_int)