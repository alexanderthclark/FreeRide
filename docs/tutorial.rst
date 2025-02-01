Market Equilibrium Analysis Using FreeRide
=========================================

Market equilibrium is a fundamental concept in economics that occurs when the quantity demanded equals the quantity supplied at a given price. This tutorial will guide you through analyzing market equilibrium using the FreeRide package, which provides tools for modeling and analyzing supply and demand curves, calculating equilibrium prices and quantities, and visualizing market dynamics.

We'll start by exploring the key concepts of supply and demand, followed by a step-by-step guide on how to use FreeRide's modules to analyze market equilibrium. By the end of this tutorial, you'll have a solid understanding of how to apply these concepts in real-world scenarios.

Key Concepts
-------------

- **Demand Curve**: A demand curve represents the relationship between the price of a good and the quantity demanded by consumers. It typically slopes downward, indicating that as the price decreases, the quantity demanded increases.
  
- **Supply Curve**: A supply curve represents the relationship between the price of a good and the quantity supplied by producers. It usually slopes upward, indicating that as the price increases, producers are willing to supply more of the good.

- **Market Equilibrium**: The point where the demand and supply curves intersect. At this price (equilibrium price), the quantity demanded equals the quantity supplied (equilibrium quantity). This is the ideal price and quantity in a competitive market.

Setup
-----

To begin, you'll need to install the FreeRide package if you haven’t already:

.. code-block:: bash

    pip install freeride

Next, let's import the necessary modules and create some demand and supply curves to work with.

Creating Demand and Supply Curves
----------------------------------

The `Demand` and `Supply` classes in FreeRide are used to model the demand and supply curves. These classes can be initialized using formulas for price as a function of quantity.

Example:

.. code-block:: python

    from freeride.curves import Demand, Supply

    # Define a demand curve
    d = Demand.from_formula('P = 12 - 1*Q')

    # Define a supply curve
    s = Supply.from_formula("P = 23 + 2*Q")

    # Visualize the demand and supply curves
    ax = d.plot(label="Demand")
    s.plot(ax=ax, label="Supply")
    ax.legend()
    ax.set_title("Demand and Supply Curves")
    plt.show()

This code defines a demand curve with the formula `P = 12 - 1*Q` and a supply curve with the formula `P = 23 + 2*Q`. These equations represent the relationship between price (P) and quantity (Q) for the demand and supply of a good.

Analyzing Market Equilibrium
-----------------------------

To analyze the market equilibrium, we need to find the price and quantity where the demand and supply curves intersect. We can do this using the `Market` class in FreeRide.

Example:

.. code-block:: python

    from freeride.market import Market

    # Create a Market object with the demand and supply curves
    m = Market(d, s)

    # Plot the market with surplus
    ax = m.plot(surplus=True)
    ax.set_title(f"Market for Tours of Pluto\nTotal Surplus = ${m.total_surplus:.2f}")
    plt.show()

In this code, the `Market` object is created by passing the demand and supply curves. The `plot()` method is then used to visualize the market with the surplus, which shows the total benefits to consumers and producers.

The plot shows the equilibrium price and quantity, where the demand and supply curves intersect. Additionally, the total surplus is calculated and displayed.

Conclusion
----------

In this tutorial, we've learned how to model and analyze market equilibrium using the FreeRide package. By defining demand and supply curves, creating a market, and visualizing the results, we can better understand how supply and demand interact in a market.

Next Steps
----------

You can extend this analysis by experimenting with different demand and supply functions, analyzing shifts in the curves, or exploring other market scenarios. The FreeRide package provides an easy-to-use framework for performing these analyses and more.

For more information, check out the FreeRide documentation or explore additional features such as consumer surplus, producer surplus, and elasticity.
