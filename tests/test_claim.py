import brownie
from brownie import chain

from tests.utils import approx


def test_basic_claim(
    fn_isolation, curve_token, vesting_contract, voting_escrow_proxy, operator
):
    chain.sleep(3600 * 24)
    chain.mine(1)
    claimer_previous_balance = curve_token.balanceOf(operator)
    claimable = vesting_contract.balanceOf(voting_escrow_proxy)
    assert claimable > 0
    voting_escrow_proxy.claim(vesting_contract, {"from": operator})
    assert approx(
        curve_token.balanceOf(operator),
        claimable + claimer_previous_balance,
        precision=1e-3,
    )


def test_non_operator_can_not_claim(
    fn_isolation, vesting_contract, voting_escrow_proxy, admin, alice
):
    chain.sleep(3600)
    chain.mine(1)
    with brownie.reverts():
        voting_escrow_proxy.claim(vesting_contract, {"from": alice})
    with brownie.reverts():
        voting_escrow_proxy.claim(vesting_contract, {"from": admin})
