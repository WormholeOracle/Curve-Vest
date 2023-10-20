import os
import json

location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(location, "ERC20.json"), "r") as f:
    ERC20_ABI = json.load(f)

with open(os.path.join(location, "VestingEscrowFactory.json"), "r") as f:
    VESTING_ESCROW_FACTORY_ABI = json.load(f)

with open(os.path.join(location, "SimpleVestingEscrow.json"), "r") as f:
    SIMPLE_VESTING_ESCROW_ABI = json.load(f)
