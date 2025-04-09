import json
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
RPC_URL = os.getenv("RPC_URL")

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL")

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "Connection to RPC failed"

PUBLIC_KEY = Web3.to_checksum_address(os.getenv("PUBLIC_KEY"))

# 0G testnet config
CHAIN_ID = 16600

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected()

# Load contract ABI and Bytecode
with open("./out/Generations.sol/NewsGenTracker.json") as f:
    contract_json = json.load(f)
    abi = contract_json["abi"]
    bytecode = contract_json["bytecode"]["object"]

# Prepare contract
contract = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(PUBLIC_KEY)

tx = contract.constructor().build_transaction({
    "from": PUBLIC_KEY,
    "nonce": w3.eth.get_transaction_count(PUBLIC_KEY),
    "gasPrice": w3.to_wei("1", "gwei"),
    "chainId": CHAIN_ID,
})

# Estimate gas more precisely
gas_estimate = w3.eth.estimate_gas(tx)
tx["gas"] = int(gas_estimate * 1.2)  # Add buffer
print(gas_estimate)

# Sign and send
signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print("Sent! Tx Hash:", tx_hash.hex())

# Wait for receipt
receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
print("Deployed at:", receipt.contractAddress)