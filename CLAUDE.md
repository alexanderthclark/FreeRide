# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FreeRide is a Python package specifically designed for **introductory microeconomics education**. It provides classes for modeling supply/demand curves, market equilibrium, game theory, and monopoly analysis using NumPy polynomials and matplotlib visualization.

**Core Philosophy**: This codebase prioritizes **elegant, readable code** above all else. As an educational tool for intro microeconomics, the code must be:
- Clear and intuitive for students and instructors
- Mathematically correct while remaining approachable
- Consistent in its patterns and conventions
- Simple enough to understand, sophisticated enough to be useful

**"Just Works" Design**: Everything should work as expected for Econ 101 tasks. For example:
- `A + B` for two demand curves performs horizontal summation (the natural operation for aggregating demand)
- All curves support piecewise functions to handle this elegantly - piecewise affine functions are closed under addition
- Users can't "fall off the edge" - operations always return valid economic objects
- Common tasks (like finding equilibrium) have intuitive interfaces that match textbook notation

**Elegant Display**: Objects should be beautiful in notebooks and terminals:
- Implement `__repr__` methods that show clean, readable representations
- Provide `_repr_latex_()` methods for Jupyter notebooks to display mathematical notation
- String representations should match what students see in textbooks (e.g., "P = 10 - 2Q")
- Make the interactive experience as polished as the code itself

**Beautiful Plotting**: Visualization must be publication-quality by default:
- All plots should look like they belong in an economics textbook
- Clean, properly labeled axes with sensible defaults
- Consistent styling across all plot types
- Support for customization while maintaining excellent defaults
- Equilibrium points, intersections, and key features should be automatically highlighted
- Colors and styles should be thoughtfully chosen for clarity and aesthetics
- Matplotlib support comes first. Eventually, we would like more interactive plots with bokeh or other libraries. 

**Error Handling Philosophy**: Since this is educational software, errors should be helpful and instructive:
- Error messages should explain what went wrong in economics terms, not just programming terms
- Guide users toward the correct usage with helpful suggestions
- Include examples in error messages when appropriate
- Never let cryptic technical errors bubble up to student users

**Performance Philosophy**: As an educational tool, code clarity always trumps performance:
- Optimize for readability and understanding, not execution speed
- Use clear variable names that match economics terminology
- Prefer explicit logic over clever shortcuts
- Performance optimizations only when they don't compromise elegance

**Documentation & Tutorials**: Beautiful Sphinx documentation is the primary goal (work in progress):
- Docstrings are good, but comprehensive RST files for Sphinx are essential
- Documentation must include embedded images showing economic graphs and concepts
- Include complete, runnable example code that teaches economics
- Each topic should have its own tutorial with visual outputs
- Build beautiful HTML docs that rival any economics textbook
- This remains an aspirational goal as the project matures

## Common Commands

### Testing
```bash
# Run all tests
python -m unittest discover tests/

# Run specific test module
python -m unittest tests.test_curves

# Run specific test class
python -m unittest tests.test_curves.TestAffine
```

### Documentation
```bash
# Install documentation dependencies
pip install -r docs/docs-requirements.txt

# Build documentation
cd docs/
make html
```

### Installation
```bash
# Install package in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

## Architecture Overview

The codebase follows a clear inheritance hierarchy built on NumPy's polynomial framework:

### Core Classes
- **PolyBase** (`base.py`): Extends `np.polynomial.Polynomial` with economics-specific methods (p/q notation, plotting, LaTeX)
- **AffineElement/QuadraticElement**: Linear and quadratic polynomial specializations

### Economic Curves (`curves.py`)
- **Demand/Supply**: Piecewise affine curves with validation (downward/upward sloping)
- **PPF**: Production Possibilities Frontier
- Support for horizontal summation (aggregating individual curves)

### Market Analysis
- **Equilibrium** (`equilibrium.py`): Solves for market equilibrium with policy interventions (tax, price controls, tariffs)
- **Monopoly** (`monopoly.py`): Profit maximization with MR=MC analysis
- **Game** (`games.py`): Normal form games with Nash equilibrium computation

### Key Design Patterns
1. **Piecewise Functions**: Both affine and quadratic curves support domain-specific segments
2. **Formula Parsing**: Create curves from strings like `"Q = 10 - 1*P"` and `"p = 1 + q"`
3. **Consistent Plotting**: All curves have `.plot()` methods with textbook-style formatting

### Intro or MVP Scope
1. **Policy Constraints**: Single intervention per equilibrium (mutual exclusivity enforced)
2. **Linear Demand**: Though demand can be piecewise, we don't need to support arbitrary functions. We're living in a linear world for demand. For costs and revenue curves, these will be quadratic.

### Testing Approach
The project uses Python's built-in `unittest` framework (not pytest). Tests are comprehensive, covering formula parsing, curve operations, equilibrium computation, and edge cases.