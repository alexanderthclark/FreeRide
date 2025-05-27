Market Equilibrium
==================

.. raw:: html

   <div style="margin-bottom: 1rem;">
     <a href="https://colab.research.google.com/github/alexanderthclark/FreeRide/blob/main/docs/notebooks/market_equilibrium.ipynb" target="_blank">
       <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab" style="margin-right: 10px;"/>
     </a>
     <a href="../notebooks/market_equilibrium.ipynb" download>
       <img src="https://img.shields.io/badge/Download-Notebook-blue?style=flat&logo=jupyter" alt="Download Notebook"/>
     </a>
   </div>


The Concept
-----------

At equilibrium:
- One price "clears" the market - quantity supplied equals quantity demanded
- There's no pressure for price to change (hence the term equilibrium)
- The sum of consumer and producer surplus is maximized

Modeling with FreeRide
----------------------

Let's create and analyze a basic market:

.. code-block:: python

   from freeride import Demand, Supply, Equilibrium

   # Create demand: P = 10 - Q
   demand = Demand("P = 10 - Q")
   
   # Create supply: P = 2 + Q
   supply = Supply("P = 2 + Q")
   
   # Find equilibrium
   market = Equilibrium(demand, supply)
   
   print(f"Equilibrium: P = ${market.p:.2f}, Q = {market.q:.0f}")
   print(f"Consumer Surplus: ${market.consumer_surplus:.2f}")
   print(f"Producer Surplus: ${market.producer_surplus:.2f}")
   
   # Plot with welfare analysis
   market.plot(surplus=True)

**Expected Output:**

.. code-block:: text

   Equilibrium: P = $6.00, Q = 4
   Consumer Surplus: $8.00
   Producer Surplus: $8.00

The plot will show the supply and demand curves intersecting at equilibrium, with 
shaded areas representing consumer and producer surplus.

Understanding Elasticity
------------------------

A common misconception is that slope determines elasticity. Let's see why that's wrong by
comparing two demand curves with the same slope but different intercepts on the price axis. The intercept is sometimes called the choke price.

Consider P = 10 - Q versus P = 12 - Q. Both have slope -1, but they differ in an important
way: the first curve hits zero quantity at P = 10, while the second doesn't reach zero until
P = 12. This means the second demand curve represents consumers who are willing to buy at 
higher prices, being less price sensitive.

.. code-block:: python

   # Two demand curves with SAME slope but DIFFERENT elasticities
   demand1 = Demand("P = 10 - Q")
   demand2 = Demand("P = 12 - Q")
   
   # Compare elasticities at P = 8
   elasticity1 = demand1.price_elasticity(8)
   elasticity2 = demand2.price_elasticity(8)
   
   print(f"At P = $8:")
   print(f"  Demand 1: Q = {demand1.q(8):.0f}, elasticity = {elasticity1:.2f}")
   print(f"  Demand 2: Q = {demand2.q(8):.0f}, elasticity = {elasticity2:.2f}")

**Expected Output:**

.. code-block:: text

   At P = $8:
     Demand 1: Q = 2, elasticity = -4.00
     Demand 2: Q = 4, elasticity = -2.00

Notice that Demand 2 is more inelastic (elasticity = -2.00) compared to Demand 1 (elasticity = -4.00) at the 
same price. This illustrates that elasticity depends on both the slope AND the position 
of the demand curve.



Try It Yourself
---------------

Click the **"Open in Colab"** button above to run this example interactively! You can:

1. Compare demand curves with the same slope but different intercepts
2. See how elasticity depends on both slope AND position
3. Explore how more/less elastic demands respond differently to supply shocks
4. Build intuition about price sensitivity

**Next:** Try the Prisoner's Dilemma tutorial at :doc:`prisoners_dilemma`!