from typing import Protocol, Tuple
import pytest
import asyncio
from pathlib import Path
import time

from hypothesis import given, settings

from starkware.starknet.compiler.compile import compile_starknet_files
from starkware.starknet.testing.starknet import Starknet

from strategy import felt, Felt

EXAMPLE_CONTRACT = Path(__file__).parent.parent / 'contracts/example.cairo'


# Need to create a module-scoped event loop, used by async fixtures.
@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()


def load_example_definition():
    return compile_starknet_files([str(EXAMPLE_CONTRACT)], debug_info=True)


@pytest.fixture(scope='module')
def example_definition():
    return load_example_definition()


# Define Protocol to type the factory fixture.
class StarknetFactory(Protocol):
    def __call__(self) -> Tuple[Starknet, int]: ...


@pytest.fixture(scope='module')
async def starknet_factory(example_definition) -> StarknetFactory:
    starknet = await Starknet.empty()
    example_addr = await starknet.deploy(example_definition)

    def _f():
        return starknet.copy(), example_addr

    return _f


@pytest.mark.asyncio
async def test_initialize(starknet_factory: StarknetFactory):
    starknet, example = starknet_factory()

    init_res = await starknet.invoke_raw(
        contract_address=example,
        selector='initialize_value',
        calldata=[42]
    )

    assert init_res.retdata == [42]


@given(value=felt(min_value=0))
@settings(max_examples=10)
@pytest.mark.asyncio
async def test_initialize_invariant(starknet_factory: StarknetFactory, value: Felt):
    starknet, example = starknet_factory()

    init_res = await starknet.invoke_raw(
        contract_address=example,
        selector='initialize_value',
        calldata=[value]
    )

    assert init_res.retdata == [value+1]