Market Equilibrium Analysis Using FreeRide
=========================================

This tutorial will guide you through analyzing market equilibrium.

We'll start by exploring the key concepts of supply and demand, followed by a step-by-step guide on how to use FreeRide's modules to analyze market equilibrium.

Setup
-----

To begin, you'll need to install the FreeRide package if you haven’t already:

.. code-block:: bash

    pip install freeride

Next, let's import the necessary modules and create some demand and supply curves to work with.

Creating Demand and Supply Curves
----------------------------------

The `Demand` and `Supply` classes in FreeRide are used to model the demand and supply curves. These classes can be initialized using formulas. Currently, a coefficient must explicitly be included. That is, `"P = 12-1*Q"` works but "`P = 12 - Q"` does not. 

Example:

.. code-block:: python

    from freeride.curves import Demand, Supply

    # Define a demand curve
    d = Demand.from_formula('P = 12 - 1*Q')

    # Define a supply curve
    s = Supply.from_formula("P = 2 + 2*Q")

    # Visualize the demand and supply curves
    ax = d.plot(label="Demand")
    s.plot(ax=ax, label="Supply")
    ax.legend()
    ax.set_title("Demand and Supply Curves")
    plt.show()

This code defines a demand curve with the formula `P = 12 - 1*Q` and a supply curve with the formula `P = 2 + 2*Q`. These equations represent the relationship between price (P) and quantity (Q) for the demand and supply of a good.

Analyzing Market Equilibrium
-----------------------------

To analyze the market equilibrium, we need to find the price and quantity where the demand and supply curves intersect. We can do this using the `Market` class in FreeRide.

Example:

.. code-block:: python

    from freeride.equilibrium import Market

    # Create a Market object with the demand and supply curves
    m = Market(d, s)

    # Plot the market with surplus
    ax = m.plot(surplus=True)
    ax.set_title(f"Market for Tours of Pluto\nTotal Surplus = ${m.total_surplus:.2f}")
    plt.show()

In this code, the `Market` object is created by passing the demand and supply curves. The `plot()` method is then used to visualize the market with the surplus, which shows the total benefits to consumers and producers.

The plot shows the equilibrium price and quantity, where the demand and supply curves intersect. Additionally, the total surplus is calculated and displayed.

