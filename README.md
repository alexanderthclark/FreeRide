# Intro-Microeconomics

This is a module (to be a package) for introductory microeconomics topics.

There are likely some bugs and surely inelegant code. Edge cases like perfectly elastic or inelastic curves are not well accounted for. 


## Use

### Curves - Demand and Supply
This is built around `Demand` and `Supply` objects, which take arguments for the *P*-intercept and the slope Δ*P*/Δ*Q*, ie the intercept and slope when the curve is written in inverse form (*P* as a function of *Q*). 

The demand curve *P* = 12 - *Q* is created with `Demand(12,-1)`. The supply curve *P* = 2 + 4*Q* is created with `Supply(2,4)`. 

### Equilibrium
Given a demand object `demand` and supply object `supply`, the equilibrium is created with `Equilibrium(demand, supply)`. Equilibria can be further modified with methods like `set_tax()`. Note `set_tax()` is an Equilibrium method, not a Demand or Supply method, meaning we bypass if it is nominally imposed on producers or consumers.  

### Aggregates
Multiple supply curves or multiple demand curves can be aggregated with the `Aggregate` class. This performs horizontal summation, disallowing negative quantities. An equilibrium can be found between an `Aggregate` object and another `Aggregate` or a `Demand` or `Supply` object. There is no specific equilibrium object for this, but instead an Aggregate method (for now). This method uses a guessing algorithm that looks for a market-clearing price.

### Public Goods
The `SocialBenefit` class aggregates a list of demand curves by summing them vertically, as is done for public goods. Combined with a social cost curve `cost`, the efficient level of provision can be found with `.efficient_outcome(cost)`. This is done by a guessing algorithm that looks for a quantity such that MSB = MSC. The private provision game can be solved with `.private_outcome(list_of_private_marginal_costs)` where the marginal costs and original demand list are ordered identically. `private_outcome_residual_demand_plots` creates a subplot grid of residual demands governing the private contribution and total consumption on the right.

### Costs

With the `Cost` class and its subclasses, you can analyze firm costs and long-run equilibrium stuff. The total cost equation _TC(q) = 50 + q + 4q^2_ is created with `TotalCost(50,1,4)`. 

## Other Comments
### Who is this for? 
Any student who is interested in solving introductory microeconomics problems and graphing might benefit from this, provided some familiarity with Python/programming. A more common use case might be from instructors or TAs, who might especially benefit from the plotting functionalities.  

### What will be added? 
I would set expectations at not much more, at least soon. But I'd like to finish this out to something that can handle the basics of a first-year undergraduate microeconomics course, at least the simpler supply and demand topics. This includes:
 1. Production Possibilities
 2. Supply Curves
 3. Demand Curves
 4. Aggregated Supply and Demand Curves
 5. Equilibrium
 6. Consumer Surplus, Producer Surplus
 7. Taxes and Subsidies and their welfare effects (DWL, incidence)
 8. Costs and Long-Run Competitive Equilibrium
 9. Public Goods
 10. Game Theory 
 11. Externalities
 12. Market Power - Monopoly and Monopsony?
 13. Market Power - Cournot?
 14. ??

### Who can help? 
If you are interested, message me. My github handle is also my gmail. Helping might take the form of contributing code or simply contributing ideas or pointing out bugs. 

I've already created more than I originally expected to create and I am due to refactor some code now that I have more holistic vision of everything.

### Why does this exist? 
I was sitting in the aiport and it seemed like something fun to do. It's also my first time writing nontrivial object-oriented code.
