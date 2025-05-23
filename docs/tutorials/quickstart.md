# Quickstart

This short guide shows how to create demand and supply curves and find an equilibrium.

```python
from freeride.curves import Demand, Supply
from freeride.equilibrium import Equilibrium

# create curves from formulas
D = Demand.from_formula("Q = 10 - 1*P")
S = Supply.from_formula("Q = 2*P")

# compute equilibrium
eq = Equilibrium(D, S)
print(eq.p, eq.q)

# plot result
ax = eq.plot()
```

![Equilibrium plot](quickstart_equilibrium.svg)
