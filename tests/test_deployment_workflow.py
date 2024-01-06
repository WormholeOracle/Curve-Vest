import brownie
import pytest

from brownie import chain, Contract
from .abis import SIMPLE_VESTING_ESCROW_ABI
from .const import  VEST_AMOUNT, VEST_DEPLOYMENT_VOTE_SCRIPT, CLAWBACK_FUNDS_VOTE_SCRIPT
from .utils import approx


def test_deployment_workflow(
    fn_isolation,
    admin,
    operator,
    vesting_escrow_proxy,
    vesting_escrow_factory,
    curve_token,
    vote_creator,
    whale_voter,
    voting_contract,
    voting_escrow,
):
    """
    This integration test aims to simulate how the DAO would allocate CRV to its 
    subDAOs through vesting escrow contracts; in addition, this test demonstrates the
    DAO's options for recourse should it want to claw back the CRV. 
    
    Steps:
    -----
    1. On mainnet, the entity requesting vested CRV would deploy the Vest Proxy 
    contract with an address under its control as the "operator" and the DAO 
    vote-controlled contract 0x40907540d8a6C65c637785e8f8B742ae6b0b9968 as the "admin".

    2. The DAO would then need to pass and execute a vote to deploy a Simple Vesting 
    Escrow contract from the Vesting Escrow Factory at 
    0xe3997288987E6297Ad550A69B31439504F513267 to the benefit of the Vest Proxy.

    3. The CRV vests linearly over 2 years, and the "operator" of the Vest Proxy can
    claim it as time passes.

    4. In a clawback situation, the DAO would vote to set its vote-controlled contract,
    the proxy's "admin", as the proxy's "operator". Only that contract could 
    claim the CRV as it vests. The former "operator" would be unable to bypass the 
    clawback.
    """
    # The Vest Proxy is deployed first through vesting_escrow_proxy

    # The factory holds CRV, which it transfers to vesting escrows when it deploys them
    assert VEST_AMOUNT <= curve_token.balanceOf(vesting_escrow_factory)

    # Next, someone creates a proposal to deploy a vesting escrow contract to 
    # vest CRV to the proxy's benefit
    create_deployment_vote_tx = voting_contract.newVote(
        VEST_DEPLOYMENT_VOTE_SCRIPT, "ipfs:metadata", {"from": vote_creator}
    )

    vote_id: int = create_deployment_vote_tx.return_value

    yes_percent: int = 10**18
    no_percent: int = 0
    vote_data: int = encode_vote_data(vote_id, yes_percent, no_percent)
    voting_contract.vote(vote_data, False, False, {"from": whale_voter})

    vote_duration: int = voting_contract.voteTime()

    chain.sleep(vote_duration)
    chain.mine(1)

    # Any account can call executeVote externally
    execute_vote_tx = voting_contract.executeVote(vote_id, {"from": operator}) 

    # This contract is actually a proxy that delegates logic to Simple Vesting Escrow
    deployment_address: str = execute_vote_tx.new_contracts[0]
    deployed_vesting_contract = Contract.from_abi(
        "Vesting Contract", deployment_address, SIMPLE_VESTING_ESCROW_ABI
    )

    assert curve_token.balanceOf(deployed_vesting_contract) == VEST_AMOUNT
    assert deployed_vesting_contract.start_time() == chain[len(chain) - 1]['timestamp']

    chain.sleep(3 * 30 * 86400)
    chain.mine(1)

    claimer_previous_balance: int = curve_token.balanceOf(operator)
    claimable: int = deployed_vesting_contract.balanceOf(vesting_escrow_proxy)
    assert claimable > 0

    vesting_escrow_proxy.claim(deployed_vesting_contract, {"from": operator})
    assert approx(
        curve_token.balanceOf(operator),
        claimable + claimer_previous_balance,
        precision=1e-3,
    )

    # A DAO vote to claw back all CRV remaining in the escrow
    create_clawback_vote_tx = voting_contract.newVote(
        CLAWBACK_FUNDS_VOTE_SCRIPT, "ipfs:metadata", {"from": vote_creator}
    )

    vote_id = create_clawback_vote_tx.return_value

    vote_data = encode_vote_data(vote_id, yes_percent, no_percent)
    voting_contract.vote(vote_data, False, False, {"from": whale_voter})

    # Operator can't steal ownership from the DAO (admin)
    with brownie.reverts(dev_revert_msg="dev: admin only"):
        vesting_escrow_proxy.commit_transfer_ownership(operator, {"from": operator})

    chain.sleep(vote_duration)
    chain.mine(1)

    execute_vote_tx = voting_contract.executeVote(vote_id, {"from": vote_creator}) 

    former_operator = operator

    # After clawback, former operator fails to claim from proxy
    with brownie.reverts(dev_revert_msg="dev: operator only"):
        vesting_escrow_proxy.claim(
            deployed_vesting_contract, vesting_escrow_factory, {"from": former_operator}
        )

    escrowed_crv = curve_token.balanceOf(deployed_vesting_contract)

    # Former operator can't bypass the clawback by calling claim on the Simple Vesting 
    # Escrow
    bypass_clawback_failure_tx = deployed_vesting_contract.claim(
        {"from": former_operator}
    )

    assert curve_token.balanceOf(deployed_vesting_contract) == escrowed_crv

    # After clawback, DAO claims vested CRV back to the factory
    factory_previous_balance: int = curve_token.balanceOf(vesting_escrow_factory)
    claimable: int = deployed_vesting_contract.balanceOf(vesting_escrow_proxy)
    assert claimable > 0

    clawback_tx = vesting_escrow_proxy.claim(
        deployed_vesting_contract, vesting_escrow_factory, {"from": admin}
    )

    assert approx(
        curve_token.balanceOf(vesting_escrow_factory),
        claimable + factory_previous_balance,
        precision=1e-3,
    )


def encode_vote_data(vote_id: int, yes_percent: int, no_percent: int) -> int:
    """ 
    Encode ballot information for voting_contract.vote's uint256 `vote_data` param:
    `yes_percent` or `no_percent` = 0 means 0% yes or no, respectively.
    `yes_percent` or `no_percent` = 10**18 means 100% yes or no, respectively.
    
    The voting contract expects the leftmost 64 bits to contain` yes_percent`, the
    next 64 bits to the right to contain `no_percent`, and the rightmost 128 bits to
    contain `vote_id`.
    """
    yes_percent_mask: int = len(bin(yes_percent)[2:])
    no_percent_mask: int = len(bin(no_percent)[2:])

    yes_percent << (64 - yes_percent_mask)
    no_percent << (64 - no_percent_mask)

    vote_data: int = yes_percent
    vote_data = vote_data << 64 | no_percent
    vote_data = vote_data << 128 | vote_id

    return vote_data