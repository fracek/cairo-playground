%lang starknet
%builtins pedersen range_check

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.storage import Storage, storage_read, storage_write

@storage_var
func _value() -> (value : felt):
end

@external
func initialize_value{
        storage_ptr : Storage*, syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        value : felt) -> (new_value : felt):
    let (existing_value) = _value.read()
    assert existing_value = 0
    _value.write(value)
    return (new_value=value)
end
