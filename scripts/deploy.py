from brownie import vest_proxy, accounts, network, web3

# https://etherscan.io/address/0x40907540d8a6C65c637785e8f8B742ae6b0b9968#readProxyContract
CURVE_DAO = "0x40907540d8a6C65c637785e8f8B742ae6b0b9968"
CRV = "0xD533a949740bb3306d119CC777fa900bA034cd52"

def test(deployer: str, claimer: str, token: str = CRV, admin: str = CURVE_DAO):
    """
    Test the Vest Proxy deployment in the local environment (NOT testnet).

    Enter any address for each of the parameters above.

    Running this script
    -------------------
    ([] params are optional)
    brownie run deploy.py test {deployer} {claimer} [{token}] [{admin}]
    """
    DEV_NETWORKS = (
        "development", 
        "mainnet-fork", 
        "anvil", 
        "anvil-fork", 
        "geth-dev", 
        "hardhat", 
        "hardhat-fork",
        )
    current_network = network.show_active()

    if current_network not in DEV_NETWORKS:
        network.disconnect()
        network.connect("development")

    if web3.isAddress(deployer):
        deployer = accounts.at(deployer, force=True)
    else:
        deployer = accounts.load(deployer)

    if web3.isAddress(claimer):
        operator = claimer
    else:
        operator = accounts.load(claimer)

    print(f"{deployer} will deploy the vest proxy")
    print(f"{operator} will operate the vest proxy")
    print(f"{admin} will be the vest proxy's admin")
    print(f"{token} will be the claimable token")

    vest_proxy_instance = vest_proxy.deploy(admin, operator, token, {"from": deployer})

    return vest_proxy_instance

def deploy(deployer: str, claimer: str, token: str = CRV, admin: str = CURVE_DAO):
    """
    Deploy a Vest Proxy contract to claim from a SimpleVestingEscrow contract.

    Parameters
    ----------
    deployer: str
        Brownie id of an account that will deploy the vest proxy. Alternatively, a 
        filepath to a JSON keystore file.

    claimer: str
        The account that will use the Vest Proxy to claim vested funds. A string 
        address will work for both multisig (smart contract) and regular accounts. A 
        Brownie id or keystore filepath will work only for regular accounts.

    token: str, default = "0xD533a949740bb3306d119CC777fa900bA034cd52"
        The contract for the token that will be claimed through the vest proxy. 
        Curve DAO's $CRV is the default.

    admin: str, default = "0x40907540d8a6C65c637785e8f8B742ae6b0b9968"
        The address that will have admin privileges over the vest proxy. The above 
        contract, which is controlled by Curve DAO votes, is the default.

    Before you run
    --------------
    Try out the `test` script above

    Add a network provider (e.g. Infura, Alchemy, etc.) to your environment:
    https://eth-brownie.readthedocs.io/en/stable/network-management.html#adding-providers

    Add the deployer account to Brownie; preferably, you would add a password-encrypted 
    keystore file:
    https://eth-brownie.readthedocs.io/en/stable/account-management.html
    
    Running this script
    -------------------
    ([] params are optional)
    brownie run --network mainnet deploy.py deploy {deployer} {claimer} [{token}] [{admin}]

    ~350k gas minimum in most cases; gas limit is estimated automatically

    Replace "mainnet" above with another network's id if necessary:
    brownie networks list

    After deploying
    ---------------
    Verify the contract's source code on Etherscan (Vyper 0.3.10):
    https://etherscan.io/verifyContract

    In tests.const, VEST_DEPLOYMENT_VOTE_SCRIPT and CLAWBACK_FUNDS_VOTE_SCRIPT guide
    you on creating some relevant vote scripts (they execute on vote passage)

    If you are claiming through a Safe multisig, use the Transaction Builder and
    call the Vest Proxy's `claim` function:
    https://help.safe.global/en/articles/40841-transaction-builder

    If you are claiming through a regular account, the resources below may be helpful:

    (In Python shell)
    >from brownie import vest_proxy
    >vest_proxy

    - https://eth-brownie.readthedocs.io/en/stable/deploy.html#the-deployment-map

    - https://eth-brownie.readthedocs.io/en/stable/core-contracts.html#interacting-with-your-contracts

    - https://eth-brownie.readthedocs.io/en/stable/interaction.html
    """
    try:
        deployer = accounts.load(deployer)
    except FileNotFoundError:
        raise FileNotFoundError(f"'{deployer}' hasn't been added to Brownie")

    try:
        operator = accounts.load(claimer)
    except FileNotFoundError:
        assert web3.isAddress(claimer), f"'{claimer}' is not a valid address, or it hasn't been added to Brownie"
        
        operator = claimer

    assert web3.isAddress(admin), f"'{admin}' is not a valid address"
    assert web3.isAddress(token), f"'{token}' is not a valid address"

    print(f"{deployer} will deploy the vest proxy")
    print(f"{operator} will operate the vest proxy")
    print(f"{admin} will be the vest proxy's admin")
    print(f"{token} will be the claimable token")

    vest_proxy_instance = vest_proxy.deploy(admin, operator, token, {"from": deployer})

    return vest_proxy_instance