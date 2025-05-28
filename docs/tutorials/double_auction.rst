Double Auction
==============

.. raw:: html

   <div style="margin-bottom: 1rem;">
     <a href="https://colab.research.google.com/github/alexanderthclark/FreeRide/blob/main/docs/notebooks/double_auction.ipynb" target="_blank">
       <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab" style="margin-right: 10px;"/>
     </a>
     <a href="../notebooks/double_auction.ipynb" download>
       <img src="https://img.shields.io/badge/Download-Notebook-blue?style=flat&logo=jupyter" alt="Download Notebook"/>
     </a>
   </div>

UnitDemand and UnitSupply
-------------------------

:class:`~freeride.double_auction.UnitDemand` represents a buyer.  Pass the 
agent's willingness to pay for each unit as positional arguments.  Likewise 
:class:`~freeride.double_auction.UnitSupply` represents a seller and takes the 
willingness to accept for each unit.  Both classes store the list of valuations 
and expose ``valuation`` for the first unit and ``endowment`` for the number of 
units held.

Example
-------

The snippet below creates two buyers and two sellers, clears the auction and 
plots the demand and supply curves.

.. code-block:: python

   from freeride.double_auction import UnitDemand, UnitSupply, DoubleAuction

   buyers = [UnitDemand(10), UnitDemand(9)]
   sellers = [UnitSupply(6), UnitSupply(4)]

   auction = DoubleAuction(*buyers, *sellers)
   print(auction)

   ax = auction.plot()

The output displays the clearing price range and quantity traded, while the plot
shows the demand and supply schedules as step functions.
