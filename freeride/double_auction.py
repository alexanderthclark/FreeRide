'''
Unit demand and unit supply for double auctions
'''

import numpy as np

class UnitAgent:
    
    def __init__(self, valuation, endowment):
        self.valuation = valuation
        self.endowment = endowment
        
        if self.valuation < 0:
            raise ValueError("No bads. Valuations must be non-negative.")
        
class UnitDemand(UnitAgent):
    
    def __init__(self, willingness_to_pay):
        super().__init__(willingness_to_pay, 0)
    
class UnitSupply(UnitAgent):
    def __init__(self, willingness_to_sell):
        super().__init__(willingness_to_sell, 1)
        
class DoubleAuction:
    
    def __init__(self, *agents):
        
        self.agents = agents
        
        key = lambda x: x[1]
        demands = sorted([(a, a.valuation) for a in agents if isinstance(a, UnitDemand)], key=key, reverse=True)
        self.demand = demands
        
        supplies = sorted([(a, a.valuation) for a in agents if isinstance(a, UnitSupply)], key=key, reverse=False)
        self.supply = supplies
        
        price_range, n_trades = self.clear()
        self.price_range = price_range
        self.p = price_range
        self.q = n_trades
        
    def clear(self):
        
        # Total quantity available
        total_q = np.sum([a.endowment for a in self.agents])
        
        # Get valuations in desc order
        self.valuations = sorted([a.valuation for a in self.agents], reverse=True)
        
        highest_valuations = self.valuations[0:total_q]
        lowest_valuations = self.valuations[total_q:]
        
        price_range = lowest_valuations[0], highest_valuations[-1]
        
        # how many suppliers should keep the good
        n_no_trade = [s for s in self.supply if s[0].valuation > price_range[1]]
        n_trades = len(self.supply) - len(n_no_trade)
        
        return price_range, n_trades
        