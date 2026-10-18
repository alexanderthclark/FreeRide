Formulas
========

Create curves from familiar equations with ``from_formula``. Variable names
are case insensitive: ``P`` and ``y`` represent the vertical variable;
``Q`` and ``x`` represent the horizontal variable.

Affine equations
----------------

Affine curves accept a constant plus a linear term. These equations create
the same demand curve:

.. code-block:: python

   from freeride.curves import Demand

   Demand.from_formula("P = 10 - 2Q")
   Demand.from_formula("10 - Q*2 = P")
   Demand.from_formula("Q = 5 - 0.5P")
   Demand.from_formula("2Q + P = 10")

An omitted coefficient means one, so ``P = 10 - Q`` is valid. Repeated
terms are added, and parentheses can group arithmetic:
``P = 2*(5-Q)`` is equivalent to ``P = 10-Q-Q``. General affine equations
must define the vertical variable as a function of the horizontal one;
``Q = 5`` does not do so.

Quadratic equations
-------------------

Quadratic curves accept equations explicitly written as ``y = ...`` or
``... = y``, with terms of degree at most two. Use ``^2``, ``**2``, or
``²`` for a square. For example:

.. code-block:: python

   from freeride.quadratic import QuadraticElement

   curve = QuadraticElement.from_formula("y = 2*x**2 + 3*x + 4")
   print(curve(2))  # 18.0

``y = 2x^2 + 3x + 4`` and ``4 + 3x + 2x² = y`` describe the same curve.
Repeated terms are added together, including repeated squared terms.

Supported syntax and errors
---------------------------

Both parsers accept decimal coefficients, signs, addition, subtraction,
explicit multiplication, and parentheses. Multiplication signs may be
omitted between a numeric coefficient and a variable, as in ``2Q``.
Write ``2*(Q+1)`` with an explicit multiplication sign before parentheses.

Use decimals such as ``0.5`` instead of fractions such as ``1/2``.
Unknown variables, function calls, extra text, nonfinite coefficients,
and terms above the supported degree raise ``FormulaParseError``.
Affine equations reject nonlinear products such as ``(Q+1)*(Q+2)``;
quadratic equations accept this product but reject cubic terms and
products involving both variables. The complete equation must be valid;
unrecognized text is never discarded.

Parser reference
----------------

.. automodule:: freeride.formula
    :members:
    :undoc-members:
    :show-inheritance:
