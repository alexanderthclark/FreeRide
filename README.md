# Intro-Microeconomics

This is a module for creating linear supply and demand curves and doing 101-style analysis and graphing.

There are likely some bugs and surely inelegant code. Producer surplus isn't calculated correctly for supply curves with a positive q-intercept. The equilibrium solver fails in poorly behaved cases. Namely, it can return negative equilibrium quantities. Edge cases like perfectly elastic or inelastic curves are not well accounted for. 


## Use

### Curves - Demand and Supply
This is built around `Demand` and `Supply` objects, which take arguments for the *P*-intercept and the slope Δ*P*/Δ*Q*, ie the intercept and slope when the curve is written in inverse form (*P* as a function of *Q*). 

The demand curve *P* = 12 - *Q* is created with `Demand(12,-1)`. The supply curve *P* = 2 + 4*Q* is created with `Supply(2,4)`. 

### Equilibrium
Given a demand object `demand` and supply object `supply`, the equilibrium is created with `Equilibrium(demand, supply)`. Equilibria can be further modified with methods like `set_tax()`. Note `set_tax()` is an Equilibrium method, not a Demand or Supply method, meaning we bypass if it is nominally imposed on producers or consumers.  

### Aggregates
Multiple supply curves or multiple demand curves can be aggregated with the `Aggregate` class. This performs horizontal summation, disallowing negative quantities. An equilibrium can be found between an `Aggregate` object and another `Aggregate` or a `Demand` or `Supply` object. There is no specific equilibrium object for this, but instead an Aggregate method (for now). This method uses a guessing algorithm that looks for a market-clearing price.

## Other Comments
### Who is this for? 
Any student who is interested in solving introductory microeconomics problems and graphing might benefit from this, provided some familiarity with Python/programming. A more common use case might be from instructors or TAs, who might especially benefit from the plotting functionalities.  

### Why does this exist? 
I was sitting in the aiport and it seemed like something fun to do. It's also my first time writing nontrivial object-oriented code. 

### What will be added? 
I would set expectations at not much more, at least soon. But I'd like to finish this out to something that can handle the basics of a first-year undergraduate microeconomics course, at least the simpler supply and demand topics. This includes:
 1. Supply Curves
 2. Demand Curves
 3. Aggregated Supply and Demand Curves
 4. Equilibrium
 5. Consumer Surplus, Producer Surplus
 6. Taxes and Subsidies and their welfare effects (DWL, incidence)
 7. Externalities
 8. Monopoly?
 9. ??

### Who can help? 
I haven't opened this up for other contributors so far. But if you are interested, message me. My github handle is also my gmail. 