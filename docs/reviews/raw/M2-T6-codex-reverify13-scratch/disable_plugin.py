# ruff: noqa
import os, inspect
from tars.validation import m2

mode = os.environ["DISABLE"]
source = inspect.getsource(m2._anchor_segment)
if mode == "coast":
    source = source.replace("if not ok:", "if False:", 1)
if mode == "burn":
    pos = source.rfind("if not ok:")
    source = source[:pos] + source[pos:].replace("if not ok:", "if False:", 1)
if mode == "extrema":
    source = source.replace("return tick_r", "return CURRENT_SOL.sol(ticks)[:3].T")
    original = m2._anchor_segment

    def anchor(*args, **kwargs):
        import sys

        m2.CURRENT_SOL = sys._getframe(1).f_locals["sol"]
        return altered(*args, **kwargs)

    exec(source, m2.__dict__)
    altered = m2._anchor_segment
    m2._anchor_segment = anchor
elif mode in ("coast", "burn"):
    exec(source, m2.__dict__)
if mode == "start":
    source = inspect.getsource(m2.dop853_reference).replace(
        "if not np.array_equal(sol.y[:, 0], y_start):", "if False:"
    )
    exec(source, m2.__dict__)
if mode == "within":

    def unsafe(err, bound):
        return bool(m2.np.all(m2.np.asarray(err) <= m2.np.asarray(bound)))

    m2.within = unsafe
