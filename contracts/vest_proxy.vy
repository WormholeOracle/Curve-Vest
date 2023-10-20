# @version 0.3.7

"""
@title Vest Proxy
@author Llama Risk
@notice Proxy contract that extends functionality of VestingEscrowSimple
"""

from vyper.interfaces import ERC20


interface VestingEscrowSimple:
    def claim(addr: address = msg.sender): payable


event Claim:
    contract: address
    recipient: address
    claimed: uint256


event RescueToken:
    to: address
    value: uint256


event SetOperator:
    operator: address


event CommitOwnership:
    admin: address


event ApplyOwnership:
    admin: address


admin: public(address)
future_admin: public(address)
operator: public(address)
token: public(address)


@external
def __init__(_admin: address, _operator: address, _token: address):
    """
    @notice Contract constructor
    @param _admin Contract admin
    @param _operator Address to receive vest
    @param _token ERC20 vest token
    """
    self.admin = _admin
    self.operator = _operator
    self.token = _token


@external
@nonreentrant("lock")
def claim(_contract: address, _recipient: address = msg.sender) -> uint256:
    """
    @notice Claim vested funds from vest contract to the operator
    @param _contract address of the vest contract
    @param _recipient address that will receive the vested tokens
    @return amount claimed
    """

    assert msg.sender == self.operator  # dev: operator only
    VestingEscrowSimple(_contract).claim()
    claimed: uint256 = ERC20(self.token).balanceOf(self)
    assert ERC20(self.token).transfer(
        _recipient, claimed, default_return_value=True
    )  # dev: transfer failed

    log Claim(_contract, _recipient, claimed)
    return claimed


@external
def rescue_token(
    _recipient: address, _amount: uint256, _erc20: address
) -> bool:
    """
    @notice Transfer `_amount` tokens from `self` to `_recipient`
    @dev Vyper does not allow underflows, so the subtraction in
         this function will revert on an insufficient balance
    @param _recipient The address to transfer to
    @param _amount The amount to be transferred
    @param _erc20 The token address to transfer
    @return bool success
    """
    assert msg.sender == self.operator  # dev: operator only
    assert _recipient != empty(address)  # dev: transfers to 0x0 are not allowed
    assert ERC20(_erc20).transfer(
        _recipient, _amount, default_return_value=True
    )  # dev: transfer failed
    log RescueToken(_recipient, _amount)

    return True


@external
def set_operator(_op: address):
    """
    @notice Set the contract operator
    @param _op Address set as the operator
    """
    assert msg.sender == self.admin  # dev: admin only
    self.operator = _op
    log SetOperator(_op)


@external
def commit_transfer_ownership(addr: address) -> bool:
    """
    @notice Transfer ownership of VestProxy to 'addr'
    @param addr Address to have ownership transferred to
    """
    assert msg.sender == self.admin  # dev: admin only
    assert addr != empty(address)  # dev: cannot set to 0x0
    self.future_admin = addr
    log CommitOwnership(addr)

    return True


@external
def accept_transfer_ownership() -> bool:
    """
    @notice Accept pending ownership transfer
    """
    assert msg.sender == self.future_admin  # dev: future admin only
    _admin: address = self.future_admin
    self.admin = _admin
    log ApplyOwnership(_admin)

    return True
