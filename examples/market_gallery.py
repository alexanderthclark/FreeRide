"""Render six Econ 101 examples and check their hand-calculated outcomes.

From the repository root, run:
    python examples/market_gallery.py --output docs/_static/market_gallery

Each figure uses Market.plot's defaults. Figure sizing and titles belong to
this gallery; curve colors, labels, viewport, and shading come from FreeRide.
"""

import argparse
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Allow the example to run directly from a source checkout.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from freeride import Demand, Market, Supply


def market_examples():
    """Return examples with independently calculated reference values."""
    demand = Demand(20, -1)
    supply = Supply(5, 0.5)
    return [
        ('equilibrium', 'Market equilibrium', Market(demand, supply),
         (10, 10, 10, 50, 25, 0, 0)),
        ('tax', 'A per-unit tax of 3', Market(demand, supply, tax=3),
         (12, 9, 8, 32, 16, 24, 3)),
        ('subsidy', 'A per-unit subsidy of 3', Market(demand, supply, tax=-3),
         (8, 11, 12, 72, 36, -36, 3)),
        ('ceiling', 'A price ceiling of 8', Market(demand, supply, ceiling=8),
         (8, 8, 6, 54, 9, 0, 12)),
        ('floor', 'A price floor of 12', Market(demand, supply, floor=12),
         (12, 12, 8, 32, 40, 0, 3)),
        ('aggregation', 'Aggregating two demands',
         Market(demand + Demand(12, -1), supply),
         (10.5, 10.5, 11, 46.25, 30.25, 0, 0)),
    ]


def checked_outcomes(market, expected):
    """Check prices, allocation, and every welfare component in an example."""
    names = ('p_consumer', 'p_producer', 'q', 'consumer_surplus',
             'producer_surplus', 'govt_revenue', 'dwl')
    actual = tuple(float(getattr(market, name)) for name in names)
    np.testing.assert_allclose(actual, expected, rtol=1e-10, atol=1e-10)
    np.testing.assert_allclose(market.total_surplus,
                               expected[3] + expected[4] + expected[5])
    return dict(zip(names, actual))


def build_gallery(output):
    """Save independent SVG/PNG figures, a contact sheet, and checked values."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    examples = market_examples()
    outcomes = {}
    sheet, axes = plt.subplots(2, 3, figsize=(15, 9), layout='constrained')
    for (name, title, market, expected), sheet_ax in zip(examples, axes.flat):
        outcomes[name] = checked_outcomes(market, expected)
        fig, ax = plt.subplots(figsize=(6.4, 4.8), layout='constrained')
        market.plot(ax=ax, surplus=True)
        ax.set_title(title, loc='left', fontweight='bold', pad=16)
        svg_path = output / f'{name}.svg'
        with plt.rc_context({'svg.fonttype': 'none'}):
            fig.savefig(svg_path, metadata={'Date': None})
        svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text().splitlines()) + '\n')
        fig.savefig(output / f'{name}.png', dpi=180)
        plt.close(fig)
        market.plot(ax=sheet_ax, surplus=True)
        sheet_ax.set_title(title, loc='left', fontweight='bold', pad=14)
    sheet.savefig(output / 'overview.png', dpi=170)
    plt.close(sheet)
    (output / 'outcomes.json').write_text(json.dumps(outcomes, indent=2) + '\n')
    return outcomes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    build_gallery(args.output)
    print('Six market examples match the hand-calculated prices and welfare.')
