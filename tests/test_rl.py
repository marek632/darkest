"""Smoke tests for the transformer RL policy."""

import pytest

torch = pytest.importorskip("torch")

from ddsim.rl.agent import make_rl_policy
from ddsim.rl.model import DDPolicyNet
from ddsim.rl.train import batch_loss, episode
from ddsim.dungeon import run_dungeon
from ddsim.policy import PolicyParams
from ddsim.strategies import STRATEGY_INDEX


def test_episode_records_trajectory_and_learns_signal():
    torch.manual_seed(0)
    net = DDPolicyNet()
    party = STRATEGY_INDEX["classic_balanced"].party
    traj, result = episode(net, party, seed=42)
    assert len(traj.logps) == len(traj.values) == len(traj.rewards) > 0
    loss, ent = batch_loss([traj], 0.01)
    assert torch.isfinite(loss)
    loss.backward()  # gradients flow
    grads = [p.grad for p in net.parameters() if p.grad is not None]
    assert grads and all(torch.isfinite(g).all() for g in grads)


def test_greedy_policy_is_deterministic_and_legal():
    torch.manual_seed(0)
    net = DDPolicyNet()
    party = STRATEGY_INDEX["classic_balanced"].party
    pol = make_rl_policy(net, greedy=True)
    a = run_dungeon(party, PolicyParams(), seed=7, policy=pol)
    b = run_dungeon(party, PolicyParams(), seed=7, policy=pol)
    assert (a.win, a.rounds, a.deaths) == (b.win, b.rounds, b.deaths)


def test_checkpoint_roundtrip(tmp_path):
    torch.manual_seed(0)
    net = DDPolicyNet()
    p = tmp_path / "net.pt"
    torch.save(net.state_dict(), p)
    net2 = DDPolicyNet()
    net2.load_state_dict(torch.load(p, weights_only=True))
    for a, b in zip(net.parameters(), net2.parameters()):
        assert torch.equal(a, b)
