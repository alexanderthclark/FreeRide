The Prisoner's Dilemma
======================

.. raw:: html

   <div style="margin-bottom: 1rem;">
     <a href="https://colab.research.google.com/github/alexanderthclark/FreeRide/blob/main/docs/notebooks/prisoners_dilemma.ipynb" target="_blank">
       <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab" style="margin-right: 10px;"/>
     </a>
     <a href="../notebooks/prisoners_dilemma.ipynb" download>
       <img src="https://img.shields.io/badge/Download-Notebook-blue?style=flat&logo=jupyter" alt="Download Notebook"/>
     </a>
   </div>

The Prisoner's Dilemma is one of the most famous examples in game theory. It illustrates why two 
rational individuals might not cooperate even when it would be in their best interest to do so.

The Scenario
------------

Two prisoners are arrested and held in separate cells. They cannot communicate with each other. 
Each has two options:

- **Cooperate** (remain silent)  
- **Defect** (betray the other)

The payoffs represent utility (higher numbers are better):

- If both cooperate: Both get utility of 3 (mutual cooperation reward)
- If both defect: Both get utility of 1 (mutual punishment)  
- If one cooperates and one defects: The cooperator gets 0 (sucker's payoff), the defector gets 5 (temptation payoff)

Modeling with FreeRide
----------------------

Let's model this game using FreeRide's game theory tools:

.. code-block:: python

   from freeride.games import Game

   game = Game.prisoners_dilemma()
   ax = game.table()
   print(game.nash())

**Expected Output:**

.. code-block:: text

   [('Defect', 'Defect')]

The visual game table will also be displayed, showing the Nash equilibrium as the actual 
strategy profile with action names.

Analysis
--------

The Nash equilibrium is **(Defect, Defect)** even though **(Cooperate, Cooperate)** would give 
both players a better outcome. This demonstrates the conflict between individual rationality 
and collective welfare.

**Key Insights:**

- Each player has a **dominant strategy** to defect
- The equilibrium outcome is **Pareto inefficient**  
- This explains many real-world cooperation problems 


Try It Yourself
---------------

Click the **"Open in Colab"** button above to run this example interactively! You can:

1. Modify the payoff values to see how they affect the equilibrium
2. Try different scenarios (what if cooperation paid more?)
3. Explore other classic games available in FreeRide

**Next:** Explore more economics concepts with FreeRide!