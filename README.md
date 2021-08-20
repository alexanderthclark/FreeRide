# Intro-Microeconomics

This is a module for creating linear supply and demand curves and doing 101-style analysis and graphing.

There are likely some bugs. Producer surplus isn't calculated correctly for supply curves with a positive q-intercept. The equilibrium solver fails in poorly behaved cases, ie it can return negative equilibrium quantities.


## Use
This is built around `Demand` and `Supply` objects, which take arguments for the *P*-intercept and the slope Δ*P*/Δ*Q*, ie the intercept and slope when the curve is written in inverse form (*P* as a function of *Q*). 

The demand curve *P* = 12 - *Q* is created with `Demand(12,-1)`. The supply curve *P* = 2 + 4*Q* is created with `Supply(2,4)`. 

Given a demand object `demand` and supply object `supply`, the equilibrium is created with `Equilibrium(demand, supply)`. Equilibria can be further modified with methods like `set_tax()`.
