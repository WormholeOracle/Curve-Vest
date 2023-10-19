import pytest
from brownie import Contract, vest_proxy

from tests.abis import ERC20_ABI, VESTING_ESCROW_FACTORY_ABI, SIMPLE_VESTING_ESCROW_ABI
from tests.const import (
    CRV_TOKEN_ADDRESS,
    VOTING_ESCROW_FACTORY_ADDRESS,
    VOTING_ESCROW_ADMIN,
    VEST_AMOUNT,
)


@pytest.fixture(scope="session")
def alice(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def bob(accounts):
    yield accounts[2]


@pytest.fixture(scope="session")
def charlie(accounts):
    yield accounts[3]


@pytest.fixture(scope="session")
def dave(accounts):
    yield accounts[4]


@pytest.fixture(scope="session")
def owner(accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def operator(accounts):
    yield accounts[9]


@pytest.fixture(scope="session")
def admin(accounts):
    yield accounts.at(VOTING_ESCROW_ADMIN, force=True)


@pytest.fixture(scope="session")
def curve_token():
    yield Contract.from_abi("CRV", CRV_TOKEN_ADDRESS, ERC20_ABI)


@pytest.fixture(scope="session")
def voting_escrow_factory():
    yield Contract.from_abi(
        "VotingEscrowFactory", VOTING_ESCROW_FACTORY_ADDRESS, VESTING_ESCROW_FACTORY_ABI
    )


@pytest.fixture(scope="module")
def voting_escrow_proxy(admin, operator):
    yield vest_proxy.deploy(admin, operator, CRV_TOKEN_ADDRESS, {"from": admin})


@pytest.fixture(scope="module")
def vesting_contract(admin, voting_escrow_factory, voting_escrow_proxy):
    deployment_tx = voting_escrow_factory.deploy_vesting_contract(
        CRV_TOKEN_ADDRESS,
        voting_escrow_proxy,
        VEST_AMOUNT,
        True,  # _can_disable
        60 * 60 * 24 * 365 * 2,  # _vesting_duration
        {"from": admin},
    )
    return Contract.from_abi(
        "Vesting Contract", deployment_tx.new_contracts[0], SIMPLE_VESTING_ESCROW_ABI
    )
