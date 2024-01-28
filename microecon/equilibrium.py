import numpy as np
import matplotlib.pyplot as plt
from microecon.curves import Demand, Supply, intersection

class Equilibrium:
    
    def __init__ (self, demand: Demand, supply: Supply):
        """Equilibrium produced by demand and supply. Initialized as market equilibrium."""
        
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