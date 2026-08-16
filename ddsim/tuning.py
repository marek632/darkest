"""Global difficulty tuning.

Calibrated so the strategies spread across roughly 30-85% win rates, which maximizes
the statistical power of strategy comparisons (see docs/DESIGN.md).
"""

ENEMY_HP_MULT = 1.45      # applied to enemy max hp
ENEMY_DMG_MULT = 1.75     # applied to enemy damage ranges
ENEMY_STRESS_MULT = 1.5  # applied to enemy stress damage
