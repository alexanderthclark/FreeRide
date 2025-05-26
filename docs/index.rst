.. raw:: html

   <div class="hero-section">
      <img src="_static/freeride-banner.png" alt="FreeRide Banner" style="max-width: 600px; margin-bottom: 2rem;">
      <h1 style="margin-top: 0;">FreeRide</h1>
      <p>Elegant Economics for Python</p>
   </div>

Welcome to FreeRide
===================

FreeRide is a Python package designed specifically for **introductory microeconomics education**. 
Built with elegance and simplicity in mind, it provides intuitive tools for modeling economic 
concepts that "just work" the way economics textbooks expect them to.

.. raw:: html

   <div class="feature-card">
      <h3>🎯 Designed for Economics 101</h3>
      <p>Every feature is crafted with introductory economics in mind. From supply and demand curves 
      to game theory, FreeRide makes economic modeling intuitive and beautiful.</p>
   </div>

   <div class="feature-card">
      <h3>✨ Elegant by Design</h3>
      <p>Clean, readable code that matches textbook notation. Operations like <code>A + B</code> 
      for demand curves naturally perform horizontal summation. Beautiful plots by default.</p>
   </div>

   <div class="feature-card">
      <h3>📊 Publication-Quality Visualizations</h3>
      <p>Every plot looks like it belongs in an economics textbook. Clean axes, automatic 
      equilibrium highlighting, and thoughtful styling make your analysis shine.</p>
   </div>

Quick Example
-------------

.. code-block:: python

   from freeride.curves import Demand, Supply
   from freeride.equilibrium import Equilibrium
   
   # Create supply and demand curves
   demand = Demand.from_formula("Q = 20 - 2*P")
   supply = Supply.from_formula("Q = -5 + 3*P")
   
   # Find equilibrium
   eq = Equilibrium(demand, supply)
   print(f"Equilibrium: P = {eq.p}, Q = {eq.q}")
   
   # Beautiful plot with one line
   eq.plot()

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



Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
.. * :ref:`modindex`
