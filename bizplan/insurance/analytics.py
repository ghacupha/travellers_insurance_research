"""Small deterministic analytics primitives; no automatic price target blending."""
from dataclasses import replace
from random import Random
from statistics import mean
from .projection import project
from .schedules import finite, nonnegative


def regression(xs, ys):
    if len(xs) != len(ys) or len(xs) < 3:
        raise ValueError('Regression needs at least three matched observations')
    finite(**{f'x{i}': x for i, x in enumerate(xs)}, **{f'y{i}': y for i, y in enumerate(ys)})
    mx, my = mean(xs), mean(ys)
    variance = sum((x-mx)**2 for x in xs)
    if variance == 0:
        raise ValueError('Predictor has no variation')
    slope = sum((x-mx)*(y-my) for x, y in zip(xs, ys))/variance
    intercept = my-slope*mx
    residual = sum((y-intercept-slope*x)**2 for x, y in zip(xs, ys))
    total = sum((y-my)**2 for y in ys)
    return dict(slope=slope, intercept=intercept, n=len(xs),
                r_squared=1-residual/total if total else None)


def dividend_value(dividends, cost_of_equity, terminal_growth):
    finite(cost_of_equity=cost_of_equity, terminal_growth=terminal_growth)
    if not dividends or cost_of_equity <= max(0, terminal_growth) or terminal_growth <= -1:
        raise ValueError('Need dividends and cost of equity > max(0, terminal growth)')
    nonnegative(**{str(i): value for i, value in enumerate(dividends)})
    pv = sum(d/(1+cost_of_equity)**i for i, d in enumerate(dividends, 1))
    terminal = dividends[-1]*(1+terminal_growth)/(cost_of_equity-terminal_growth)
    return dict(equity_value=pv+terminal/(1+cost_of_equity)**len(dividends),
                terminal_present_value=terminal/(1+cost_of_equity)**len(dividends))


def monte_carlo(opening, drivers, years, draws=1000, seed=7, catastrophe_sigma=0.02):
    """Illustrative truncated-normal cat ratio, held constant across each path.

    Not a calibrated catastrophe model: no geographic events, tails or dependencies.
    Runs the same schedule engine as deterministic scenarios.
    """
    if isinstance(draws, bool) or not isinstance(draws, int) or draws < 2:
        raise ValueError('At least two integer draws required')
    nonnegative(catastrophe_sigma=catastrophe_sigma)
    rng = Random(seed)
    values = []
    for _ in range(draws):
        d = replace(drivers, catastrophe_loss_ratio=max(0, rng.gauss(drivers.catastrophe_loss_ratio, catastrophe_sigma)))
        values.append(sum(row['underwriting_result'] for row in project(opening, d, years)))
    values.sort()
    return dict(draws=draws, seed=seed, status='illustrative',
                measure='undiscounted cumulative underwriting result', mean=mean(values),
                p05=values[int((draws-1)*.05)], p50=values[int((draws-1)*.5)],
                p95=values[int((draws-1)*.95)], catastrophe_sigma=catastrophe_sigma)
