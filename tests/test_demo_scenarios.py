"""Structural checks on the coding scenarios: each trap's evidence is really planted where it says."""

from demo.coding_session.scenarios import SCENARIOS


def test_traps_are_well_formed():
    for sc in SCENARIOS:
        names = [t.name for t in sc.traps]
        assert len(names) == len(set(names)), sc.name
        for t in sc.traps:
            assert 1 <= t.planted_at < t.exchange <= len(sc.exchanges), (sc.name, t.name)
            user, reply = sc.exchanges[t.planted_at - 1]
            assert t.required in user + reply, (sc.name, t.name, "required text not planted")
            # the trap question itself must not give the answer away
            assert t.required not in sc.exchanges[t.exchange - 1][0], (sc.name, t.name)
            if t.stale:
                earlier = " ".join(u + r for u, r in sc.exchanges[: t.planted_at - 1])
                assert t.stale in earlier, (sc.name, t.name, "stale form never appeared")
            assert t.name in sc.kinds, (sc.name, t.name)
