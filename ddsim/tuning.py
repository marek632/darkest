"""Global difficulty tuning.

Official monster stat cards are not public, so enemy numbers are
approximations calibrated here so that strategy win rates spread across
roughly 30-85%, which maximizes the statistical power of strategy
comparisons (see docs/DESIGN.md and docs/RULES_AUDIT.md).
"""

ENEMY_HP_MULT = 0.85      # applied to enemy max hp
ENEMY_DMG_MULT = 1.1     # applied to enemy damage ranges
ENEMY_STRESS_MULT = 1.0  # applied to enemy stress damage (0-10 track)
