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

The payoffs depend on what both players choose:

- If both cooperate: Both get 3 years in prison
- If both defect: Both get 1 year in prison  
- If one cooperates and one defects: The cooperator gets 0 years, the defector gets 5 years

Modeling with FreeRide
----------------------

Let's model this game using FreeRide's game theory tools:

.. code-block:: python

   from freeride.games import PrisonersDilemma

   # Create the classic Prisoner's Dilemma game
   game = PrisonersDilemma(cooperate_cooperate=(3, 3), 
                          defect_defect=(1, 1),
                          cooperate_defect=(0, 5), 
                          defect_cooperate=(5, 0))

   # Display the game table
   print("Prisoner's Dilemma Payoff Matrix:")
   print(game)

   # Find Nash equilibrium
   print("Nash Equilibrium:")
   print(game.nash_equilibrium())

**Expected Output:**

.. code-block:: text

   Prisoner's Dilemma Payoff Matrix:
             Cooperate  Defect
   Cooperate    (3,3)   (0,5)
   Defect       (5,0)   (1,1)

   Nash Equilibrium:
   (Defect, Defect)

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