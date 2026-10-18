Welcome to FreeRide
===================

.. image:: _static/freeride-banner.png
   :alt: FreeRide Banner
   :align: center
   :width: 600px

FreeRide is a Python package designed specifically for **introductory microeconomics**. 
Built with simplicity in mind, it provides intuitive tools for modeling economic 
concepts that "just work" the way economics students expect them to.

.. raw:: html

   <div class="feature-card">
      <h3>🎯 Designed for Economics 101</h3>
      <p>Every feature is crafted with introductory economics in mind. The focus is on simple cases, like linear or piecewise-linear demand curves, that illustrate key concepts.</p>
   </div>

   <div class="feature-card">
      <h3>✨ Intuitive by Design</h3>
      <p>Clean, readable code that matches conventional notation. Operations like <code>a + b</code> 
      for demand curves naturally perform horizontal summation.</p>
   </div>

   <div class="feature-card">
      <h3>📊 Learn Visually</h3>
      <p>Plotting capabilities are emphasized. Every plot looks like it belongs in an economics textbook. Clean axes, automatic equilibrium highlighting, and thoughtful styling make your analysis shine.</p>
   </div>

Installation
------------

Install FreeRide using pip:

.. code-block:: bash

   pip install freeride

Quick Example
-------------

.. code-block:: python

   from freeride import Demand, Supply
   
   # Create supply and demand curves
   demand = Demand.from_formula("Q = 20 - 2*P")
   supply = Supply.from_formula("Q = -5 + 3*P")
   
   # Find equilibrium using the intersection operator
   market = demand & supply
   
   # Beautiful plot with shaded surplus
   market.plot(surplus=True)

   # Inspect the equilibrium
   print(f"Price: {market.p:.2f}, quantity: {market.q:.2f}")
   print(f"Consumer surplus: {market.consumer_surplus:.2f}")
   print(f"Producer surplus: {market.producer_surplus:.2f}")

**Output:**

.. code-block:: text

   Price: 5.00, quantity: 10.00
   Consumer surplus: 25.00
   Producer surplus: 16.67

The plot shows the supply and demand curves with the equilibrium point clearly marked, 
and the consumer and producer surplus areas shaded:

.. image:: _static/quick_example_plot.svg
   :alt: Market equilibrium plot with supply and demand curves and shaded surplus
   :align: center
   :width: 600px

Basic Tax Example
-----------------

We can easily add a tax to the market and visualize its effects.

.. code-block:: python

   # Apply a $2.50 tax
   market.tax = 2.5
   market.plot(surplus=True)

This plot shows the higher price paid by consumers, the lower price
received by producers, and the shaded tax revenue rectangle.

.. image:: _static/tax_example_plot.svg
   :alt: Market plot with tax revenue shaded
   :align: center
   :width: 600px

.. toctree::
   :maxdepth: 1
   :caption: Contents

   curves
   costs
   formula
   exceptions
   plotting
   games
   tutorials/quickstart

.. toctree::
   :maxdepth: 1
   :caption: Tutorials

   tutorials/double_auction
   tutorials/market_equilibrium
   tutorials/market_gallery
   tutorials/price_controls
   tutorials/prisoners_dilemma



Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. * :ref:`modindex`
