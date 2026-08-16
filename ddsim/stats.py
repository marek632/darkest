"""Statistics helpers: Wilson intervals and two-proportion z-tests.

Implemented from first principles so the simulator has no dependencies
beyond the standard library.
"""

from __future__ import annotations

import math


def wilson_ci(successes, n, z=1.96):
    """95% Wilson score interval for a binomial proportion."""
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def _norm_sf(z):
    """Survival function of the standard normal."""
    return 0.5 * math.erfc(z / math.sqrt(2))


def two_proportion_z(s1, n1, s2, n2):
    """Two-sided two-proportion z-test.

    Returns (z, p_value). Positive z means sample 1 has the higher rate.
    """
    if n1 == 0 or n2 == 0:
        return 0.0, 1.0
    p1, p2 = s1 / n1, s2 / n2
    pooled = (s1 + s2) / (n1 + n2)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    if se == 0:
        return 0.0, 1.0
    z = (p1 - p2) / se
    return z, 2 * _norm_sf(abs(z))


def mean_std(values):
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    m = sum(values) / n
    var = sum((v - m) ** 2 for v in values) / (n - 1) if n > 1 else 0.0
    return m, math.sqrt(var)
