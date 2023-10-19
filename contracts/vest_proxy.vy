# @version 0.3.7
"""
@title Vest Proxy
@author Llama Risk
@notice Proxy contract that extends functionality of VestingEscrowSimple
"""

from vyper.interfaces import ERC20

interface VestingEscrowSimple:
    def claim(addr: address = msg.sender): payable
    def start_time() -> uint256: view
    def end_time() -> uint256: view
    def disabled_at(arg0: address) -> uint256: view
    def total_claimed(arg0: address) -> uint256: view
    def initial_locked(arg0: address) -> uint256: view


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

event Revoked:
    operator: address

event ClawBack:
    contract: address
    recipient: address
    retrieved: uint256

admin: public(address)
future_admin: public(address)
operator: public(address)
token: public(address)
balanceOf: public(HashMap[address, uint256])
revoked_at: public(uint256)


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


@internal
@view
def _total_vested_of(_contract: address, _time: uint256 = block.timestamp) -> uint256:   
    start: uint256 = VestingEscrowSimple(_contract).start_time()
    end: uint256 = VestingEscrowSimple(_contract).end_time()
    locked: uint256 = VestingEscrowSimple(_contract).initial_locked(self)
    if _time < start:
        return 0
    return min(locked * (_time - start) / (end - start), locked)


@external
@nonreentrant('lock')
def claim(_contract: address, _recipient: address = msg.sender):
    """
    @notice Claim vested funds from vest contract to the operator
    @param _contract address of the vest contract
    @param _recipient address that will receive the vested tokens
    """

    assert self.revoked_at == 0
    assert msg.sender == self.operator # dev: operator only
    t: uint256 = VestingEscrowSimple(_contract).disabled_at(self)
    if t == 0:
        t = block.timestamp
    claimed: uint256 = VestingEscrowSimple(_contract).total_claimed(self)
    claimable: uint256 = self._total_vested_of(_contract, t) - claimed
    claimed += claimable
    VestingEscrowSimple(_contract).claim()

    assert ERC20(self.token).transfer(_recipient, claimable)
    
    log Claim(_contract, _recipient, claimable)


@external
def revoke():
    """
    @notice Revokes the vesting contract, operation is final
    """
    assert self.revoked_at == 0
    self.revoked_at = block.timestamp
    self.operator = empty(address)

    log Revoked(self.operator)


@external
def claw_back(_contract: address, _recipient: address):
    """
    @notice Retrieve vested funds after the stream has been revoked
    @param _contract address of the vest contract
    @param _recipient address that will receive the funds
    """
    assert self.revoked_at != 0
    assert msg.sender == self.admin
    VestingEscrowSimple(_contract).claim()
    retrieved: uint256 = ERC20(self.token).balanceOf(self)
    assert ERC20(self.token).transfer(_recipient, retrieved)

    log ClawBack(_contract, _recipient, retrieved)


@external
def rescue_token(_to: address, _value: uint256, _erc20: address ) -> bool:
    """
    @notice Transfer `_value` tokens from `self` to `_to`
    @dev Vyper does not allow underflows, so the subtraction in
         this function will revert on an insufficient balance
    @param _to The address to transfer to
    @param _value The amount to be transferred
    @param _erc20 The token address to transfer
    @return bool success
    """
    assert msg.sender == self.operator # dev: operator only
    assert _to != ZERO_ADDRESS  # dev: transfers to 0x0 are not allowed   
    assert ERC20(_erc20).transfer(_to, _value)
    log RescueToken(_to, _value)

    return True


@external
def set_operator(_op: address):
    """
    @notice Set the contract operator
    @param _op Address set as the operator
    """
    assert self.revoked_at == 0
    assert msg.sender == self.admin # dev: admin only    
    self.operator = _op
    log SetOperator(_op)


@external
def commit_transfer_ownership(addr: address) -> bool:
    """
    @notice Transfer ownership of VestProxy to 'addr'
    @param addr Address to have ownership transferred to
    """
    assert msg.sender == self.admin  # dev: admin only   
    self.future_admin = addr
    log CommitOwnership(addr)

    return True


@external
def apply_transfer_ownership() -> bool:
    """
    @notice Apply pending ownership transfer
    """
    assert msg.sender == self.admin  # dev: admin only
    _admin: address = self.future_admin
    assert _admin != ZERO_ADDRESS  # dev: admin not set
    self.admin = _admin
    log ApplyOwnership(_admin)

    return True