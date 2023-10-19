import brownie
import pytest


def test_set_operator(fn_isolation, voting_escrow_proxy, admin, operator, alice):
    assert voting_escrow_proxy.admin() == admin
    assert voting_escrow_proxy.operator() == operator
    voting_escrow_proxy.set_operator(alice, {"from": admin})
    assert voting_escrow_proxy.operator() == alice
    with brownie.reverts():
        voting_escrow_proxy.set_operator(alice, {"from": alice})


def test_transfer_ownership(fn_isolation, voting_escrow_proxy, admin, alice):
    with brownie.reverts():
        voting_escrow_proxy.commit_transfer_ownership(alice, {"from": alice})

    assert voting_escrow_proxy.admin() == admin
    voting_escrow_proxy.commit_transfer_ownership(alice, {"from": admin})
    assert voting_escrow_proxy.future_admin() == alice
    assert voting_escrow_proxy.admin() == admin

    with brownie.reverts():
        voting_escrow_proxy.apply_transfer_ownership({"from": alice})  # not admin yet

    voting_escrow_proxy.apply_transfer_ownership({"from": admin})
    assert voting_escrow_proxy.admin() == alice


def test_no_transfer_to_zero_address(
    fn_isolation, voting_escrow_proxy, admin, operator, alice
):
    assert voting_escrow_proxy.admin() == admin
    with brownie.reverts():
        voting_escrow_proxy.apply_transfer_ownership({"from": admin})
