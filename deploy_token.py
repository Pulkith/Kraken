import os
import json
import subprocess
from pathlib import Path

def run_forge_create(contract_name, constructor_args=None):
    cmd = ["forge", "create", "--rpc-url", os.environ["RPC_URL"], "--private-key", os.environ["PRIVATE_KEY"], contract_name]

    if constructor_args:
        for arg in constructor_args:
            cmd.extend(["--constructor-args", arg])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error deploying", contract_name)
        print(result.stderr)
        raise RuntimeError(result.stderr)

    print(result.stdout)
    # Parse address
    for line in result.stdout.splitlines():
        if "Deployed to:" in line:
            return line.split("Deployed to:")[-1].strip()

    raise ValueError("Address not found in forge output")

def main():
    print("Deploying true contracts to foundry chainlet...")

    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Deploy TRUEToken
    print("Deploying TRUEToken...")
    deployer_address = os.environ["DEPLOYER_ADDRESS"]
    true_token_address = run_forge_create("src/TRUEToken.sol:TRUEToken", [deployer_address])
    print("TRUEToken deployed to:", true_token_address)

    # Deploy trueVerification
    print("Deploying trueVerification...")
    verification_address = run_forge_create("src/trueVerification.sol:trueVerification", [true_token_address])
    print("trueVerification deployed to:", verification_address)

    print("foundry contracts deployed successfully")

    deployment_info = {
        "trueToken": true_token_address,
        "verification": verification_address
    }

    print("Contract addresses:", json.dumps(deployment_info, indent=2))

    with open(logs_dir / "foundry-deployment.json", "w") as f:
        json.dump(deployment_info, f, indent=2)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Deployment failed:", e)
        exit(1)