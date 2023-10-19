import os
import json

location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

ERC20_ABI = json.load(open(os.path.join(location, "ERC20.json"), "r"))
VESTING_ESCROW_FACTORY_ABI = json.load(
    open(os.path.join(location, "VestingEscrowFactory.json"), "r")
)
SIMPLE_VESTING_ESCROW_ABI = json.load(
    open(os.path.join(location, "SimpleVestingEscrow.json"), "r")
)
