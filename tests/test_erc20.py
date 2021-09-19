from typing import Protocol, Tuple
import pytest
import asyncio
from pathlib import Path

from hypothesis import given, settings

from starkware.starknet.compiler.compile import compile_starknet_files
from starkware.starknet.testing.starknet import Starknet

from strategy import felt, Felt

ERC20_CONTRACT = Path(__file__).parent.parent / 'contracts/erc20.cairo'

ALICE = 1111
BOB = 2222
TOTAL_SUPPLY = 1000


# Need to create a module-scoped event loop, used by async fixtures.
@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()


def load_erc20_definition():
    return compile_starknet_files([str(ERC20_CONTRACT)], debug_info=True)


@pytest.fixture(scope='module')
def erc20_definition():
    return load_erc20_definition()


# Define Protocol to type the factory fixture.
class StarknetFactory(Protocol):
    def __call__(self) -> Tuple[Starknet, int]: ...


@pytest.fixture(scope='module')
async def starknet_factory(erc20_definition) -> StarknetFactory:
    starknet = await Starknet.empty()
    erc20_addr = await starknet.deploy(erc20_definition)
    await starknet.invoke_raw(
        contract_address=erc20_addr,
        selector='initialize',
        calldata=[ALICE, TOTAL_SUPPLY]
    )

    def _f():
        return starknet.copy(), erc20_addr

    return _f


@given(amount=felt(max_value=TOTAL_SUPPLY))
@settings(max_examples=10, deadline=1000)
@pytest.mark.asyncio
async def test_initialize_invariant(starknet_factory: StarknetFactory, amount: Felt):
    starknet, erc20 = starknet_factory()

    pre_alice_balance, pre_bob_balance = await _get_balances(starknet, erc20)

    await starknet.invoke_raw(
        contract_address=erc20,
        selector='transfer_from',
        calldata=[ALICE, BOB, amount],
    )

    post_alice_balance, post_bob_balance = await _get_balances(starknet, erc20)

    # balances changed
    assert post_alice_balance + amount == pre_alice_balance
    assert pre_bob_balance + amount == post_bob_balance

    # transfer does not create new tokens
    assert pre_alice_balance + pre_bob_balance == TOTAL_SUPPLY
    assert post_alice_balance + post_bob_balance == TOTAL_SUPPLY


async def _get_balances(starknet: Starknet, erc20: int) -> Tuple[int, int]:
    alice_balance = await starknet.invoke_raw(
        contract_address=erc20,
        selector='balance_of',
        calldata=[ALICE],
    )

    bob_balance = await starknet.invoke_raw(
        contract_address=erc20,
        selector='balance_of',
        calldata=[BOB],
    )

    return alice_balance.retdata[0], bob_balance.retdata[0]