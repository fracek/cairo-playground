# ERC20
#
# This contract is used to show how to use property based testing with Cairo.
# It should not be used for a real ERC20 contract.
%lang starknet
%builtins pedersen range_check

from starkware.cairo.common.dict import dict_new, dict_read, dict_write
from starkware.cairo.common.dict_access import DictAccess
from starkware.cairo.common.math import assert_nn, assert_not_zero, assert_250_bit, assert_in_range
from starkware.cairo.common.registers import get_fp_and_pc
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.storage import Storage, storage_read, storage_write
from starkware.starknet.common.syscalls import get_caller_address

@storage_var
func _balances(user : felt) -> (balance : felt):
end

@external
func initialize{
        storage_ptr : Storage*, syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        owner : felt, total_supply : felt):
    assert_nn(total_supply)
    assert_250_bit(total_supply)
    _balances.write(owner, total_supply)
    return ()
end

@external
func transfer_from{
        storage_ptr : Storage*, syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        sender : felt, receiver : felt, amount : felt):
    let (sender_balance) = _balances.read(sender)
    let (receiver_balance) = _balances.read(receiver)

    let new_sender_balance = sender_balance - amount
    let new_receiver_balance = receiver_balance + amount

    assert_nn(new_sender_balance)
    assert_250_bit(new_sender_balance)
    assert_250_bit(new_receiver_balance)

    _balances.write(sender, new_sender_balance)
    _balances.write(receiver, new_receiver_balance)

    return ()
end

@view
func balance_of{
        storage_ptr : Storage*, syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        user : felt) -> (balance : felt):
    let (balance) = _balances.read(user)
    return (balance=balance)
end
