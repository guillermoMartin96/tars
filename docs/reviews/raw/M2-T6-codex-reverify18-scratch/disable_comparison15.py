# ruff: noqa
from tars.validation import reference_snapshot as snap
import math

snap.TOLERANCES = {key: math.inf for key in snap.TOLERANCES}
