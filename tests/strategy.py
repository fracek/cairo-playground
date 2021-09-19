import hypothesis.strategies as st
from starkware.cairo.lang.cairo_constants import DEFAULT_PRIME

Felt = int


def felt(min_value=None, max_value=None) -> st.SearchStrategy[Felt]:
    if min_value is not None:
        min_value = max(min_value, -DEFAULT_PRIME/2)
    else:
        min_value = -DEFAULT_PRIME/2

    if max_value is not None:
        max_value = min(max_value, DEFAULT_PRIME/2)
    else:
        max_value = DEFAULT_PRIME/2

    return st.integers(min_value=min_value, max_value=max_value)


def felt_u256(min_value=None, max_value=None) -> st.SearchStrategy[Felt]:
    if min_value is not None:
        min_value = max(0, min_value)
    else:
        min_value = 0

    if max_value is not None:
        max_value = min(2**256 - 1, max_value)
    else:
        max_value = 2**256 - 1

    return felt(min_value=min_value, max_value=max_value)
