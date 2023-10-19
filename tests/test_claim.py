import brownie
import pytest
from brownie import chain


def test_basic_claim(
    fn_isolation, curve_token, vesting_contract, voting_escrow_proxy, operator
):
    chain.sleep(3600)
    chain.mine(1)
    claimable = vesting_contract.balanceOf(voting_escrow_proxy)
    assert claimable > 0
    claimer_previous_balance = curve_token.balanceOf(operator)
    voting_escrow_proxy.claim(vesting_contract, {"from": operator})
    assert curve_token.balanceOf(operator) == claimable + claimer_previous_balance


def test_non_operator_can_not_claim(
    fn_isolation, vesting_contract, voting_escrow_proxy, admin, alice
):
    chain.sleep(3600)
    chain.mine(1)
    with brownie.reverts():
        voting_escrow_proxy.claim(vesting_contract, {"from": alice})
    with brownie.reverts():
        voting_escrow_proxy.claim(vesting_contract, {"from": admin})
