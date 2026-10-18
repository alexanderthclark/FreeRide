Double Auction
==============

:download:`Download the notebook <../notebooks/double_auction.ipynb>`

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
