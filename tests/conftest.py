import pytest
from brownie import Contract, vest_proxy

from tests.abis import (
    ERC20_ABI, 
    VESTING_ESCROW_FACTORY_ABI, 
    SIMPLE_VESTING_ESCROW_ABI, 
    VOTING_ESCROW_ABI,
    )
from tests.const import (
    CRV_TOKEN_ADDRESS,
    BAT_TOKEN_ADDRESS,
    VEST_AMOUNT,
    VESTING_ESCROW_FACTORY_ADDRESS,
    VESTING_ESCROW_FACTORY_ADMIN,
    FACTORY_ADMIN_IMPLEMENTATION,
    VOTING_ESCROW_ADDRESS,
    VOTING_CONTRACT_PROXY,
    VOTING_CONTRACT_IMPLEMENTATION,
    WHALE_VOTER,
    VOTE_CREATOR,
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
def admin():
    yield Contract.from_explorer(
        VESTING_ESCROW_FACTORY_ADMIN, as_proxy_for=FACTORY_ADMIN_IMPLEMENTATION
    )


@pytest.fixture(scope="session")
def curve_token():
    yield Contract.from_abi("CRV", CRV_TOKEN_ADDRESS, ERC20_ABI)


@pytest.fixture(scope="session")
def transfer_false_token():
    yield Contract.from_abi("BAT", BAT_TOKEN_ADDRESS, ERC20_ABI)


@pytest.fixture(scope="session")
def vesting_escrow_factory():
    yield Contract.from_abi(
        "VestingEscrowFactory",
        VESTING_ESCROW_FACTORY_ADDRESS,
        VESTING_ESCROW_FACTORY_ABI,
    )


@pytest.fixture(scope="module")
def vesting_escrow_proxy(admin, operator):
    yield vest_proxy.deploy(admin, operator, CRV_TOKEN_ADDRESS, {"from": admin})


@pytest.fixture(scope="module")
def vesting_contract(admin, vesting_escrow_factory, vesting_escrow_proxy):
    deployment_tx = vesting_escrow_factory.deploy_vesting_contract(
        CRV_TOKEN_ADDRESS,
        vesting_escrow_proxy,
        VEST_AMOUNT,
        True,  # _can_disable
        60 * 60 * 24 * 365 * 2,  # _vesting_duration
        {"from": admin},
    )
    return Contract.from_abi(
        "Vesting Contract", deployment_tx.new_contracts[0], SIMPLE_VESTING_ESCROW_ABI
    )


@pytest.fixture(scope="session")
def voting_escrow():
    yield Contract.from_abi("Voting Escrow", VOTING_ESCROW_ADDRESS, VOTING_ESCROW_ABI)


@pytest.fixture(scope="session")
def voting_contract():
    yield Contract.from_explorer(
        VOTING_CONTRACT_PROXY, as_proxy_for=VOTING_CONTRACT_IMPLEMENTATION
    )


@pytest.fixture(scope="session")
def vote_creator(accounts):
    yield accounts.at(VOTE_CREATOR, force=True)


@pytest.fixture(scope="session")
def whale_voter(accounts):
    yield accounts.at(WHALE_VOTER, force=True)