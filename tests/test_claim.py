import brownie
from brownie import chain

from tests.const import VEST_AMOUNT
from tests.utils import approx


def test_basic_claim(
    fn_isolation, curve_token, vesting_contract, vesting_escrow_proxy, operator
):
    chain.sleep(3600 * 24)
    chain.mine(1)
    claimer_previous_balance = curve_token.balanceOf(operator)
    claimable = vesting_contract.balanceOf(vesting_escrow_proxy)
    assert claimable > 0
    vesting_escrow_proxy.claim(vesting_contract, {"from": operator})
    assert approx(
        curve_token.balanceOf(operator),
        claimable + claimer_previous_balance,
        precision=1e-3,
    )


def test_claim_to_third_party(
    fn_isolation, curve_token, vesting_contract, vesting_escrow_proxy, operator, alice
):
    chain.sleep(3600 * 24)
    chain.mine(1)
    recipient_previous_balance = curve_token.balanceOf(alice)
    claimable = vesting_contract.balanceOf(vesting_escrow_proxy)
    assert claimable > 0
    vesting_escrow_proxy.claim(vesting_contract, alice, {"from": operator})
    assert approx(
        curve_token.balanceOf(alice),
        claimable + recipient_previous_balance,
        precision=1e-3,
    )


def test_non_operator_can_not_claim(
    fn_isolation, vesting_contract, vesting_escrow_proxy, admin, alice
):
    chain.sleep(3600)
    chain.mine(1)
    with brownie.reverts(dev_revert_msg="dev: operator only"):
        vesting_escrow_proxy.claim(vesting_contract, {"from": alice})
    with brownie.reverts(dev_revert_msg="dev: operator only"):
        vesting_escrow_proxy.claim(vesting_contract, {"from": admin})


def test_claw_back_flow(
    fn_isolation, vesting_contract, curve_token, vesting_escrow_proxy, admin, operator
):
    chain.sleep(3600 * 24 * 7)
    chain.mine(1)
    vesting_escrow_proxy.set_operator(admin, {"from": admin})
    with brownie.reverts(dev_revert_msg="dev: operator only"):
        vesting_escrow_proxy.claim(vesting_contract, {"from": operator})
    admin_previous_balance = curve_token.balanceOf(admin)
    claimable = vesting_contract.balanceOf(vesting_escrow_proxy)
    assert claimable > 0
    vesting_escrow_proxy.claim(vesting_contract, {"from": admin})
    assert approx(
        curve_token.balanceOf(admin),
        claimable + admin_previous_balance,
        precision=1e-3,
    )
