"""Reinforcement-learning hero AI (transformer policy).

Architecture (see model.py):
* a SHARED transformer trunk encodes the battle state as a set of entity
  tokens (every hero and monster) plus a global token,
* a SHARED value head scores the game state (one model for all heroes),
* EACH HERO CLASS has its OWN policy head that scores that hero's legal
  actions against the encoded state — so different characters can learn
  different strategies while reading the same shared representation.
"""
