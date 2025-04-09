import json
import os
import subprocess
from datetime import datetime
from math import sqrt
from dotenv import load_dotenv
from web3 import Web3

# Load environment variables
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = Web3.to_checksum_address(os.getenv("PUBLIC_KEY"))
RPC_URL = os.getenv("RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Initialize web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.isConnected(), "Could not connect to RPC."

# Load the contract ABI from the compiled artifact (assumes it was built by Foundry in out/ArticleRegistry.sol/ArticleRegistry.json)
with open("out/ArticleRegistry.sol/ArticleRegistry.json") as f:
    artifact = json.load(f)
abi = artifact["abi"]

# Create contract object
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

#############################################
# PART 1: UPLOAD JSON FILE TO 0G STORAGE
#############################################
def upload_json_to_storage(file_path: str) -> str:
    """
    Simulates uploading a JSON file to 0G storage by invoking the CLI.
    In a real system, this call would interact with the 0G Storage CLI/API.
    """
    try:
        # Example using subprocess – ensure that the CLI binary is in ./cli (adjust path as needed)
        result = subprocess.run(
            ["./cli", "upload", "--file", file_path],
            check=True,
            capture_output=True,
            text=True
        )
        # Assume the CLI prints out the blob root (file URI)
        file_uri = result.stdout.strip()
        print("File uploaded. URI/Blob Root:", file_uri)
        return file_uri
    except Exception as e:
        # Fallback: if no CLI available, simulate a file URI from filename and timestamp
        simulated_uri = "0xSIMULATED" + os.path.basename(file_path)
        print("Simulating upload. Using URI:", simulated_uri)
        return simulated_uri

#############################################
# PART 2: RECORD FILE REFERENCE ON CHAIN
#############################################
def register_file_on_chain(file_uri: str):
    """
    Calls the smart contract function to store the file pointer.
    """
    # Get the latest nonce
    nonce = w3.eth.get_transaction_count(PUBLIC_KEY)
    # Build the transaction: note that no gas estimation is used here, but you can add that.
    tx = contract.functions.uploadFile(file_uri).buildTransaction({
        "from": PUBLIC_KEY,
        "nonce": nonce,
        "gasPrice": w3.toWei("80", "gwei"),
        "chainId": w3.eth.chain_id
    })
    # Optionally, you can estimate gas:
    gas_estimate = w3.eth.estimateGas(tx)
    tx["gas"] = int(gas_estimate * 1.2)

    # Sign and send the transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print("Transaction sent, tx hash:", tx_hash.hex())
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    print("File reference recorded on-chain in block", receipt.blockNumber)

#############################################
# PART 3: SEMANTIC SEARCH OVER THE JSON DATA
#############################################
def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two equal-length lists."""
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sqrt(sum(a * a for a in vec1))
    norm2 = sqrt(sum(b * b for b in vec2))
    return dot / (norm1 * norm2) if norm1 and norm2 else 0

def semantic_search(query_embedding, min_pub_date: str, top_x: int, json_path: str):
    """
    Given a query embedding (a list of floats), a minimum publication date (ISO string),
    and top_x (number of results), load the JSON file (with articles) and
    return the top_x articles (as dicts) sorted by cosine similarity.
    Only articles with metadata.pub_date >= min_pub_date are considered.
    """
    # Convert min_pub_date to datetime object
    min_date = datetime.fromisoformat(min_pub_date.replace("Z", "+00:00"))

    # Load the JSON file
    with open(json_path, "r") as f:
        articles = json.load(f)
    
    filtered = []
    for article in articles:
        # Extract pub_date from article metadata
        pub_date_str = article.get("metadata", {}).get("pub_date", "")
        if not pub_date_str:
            continue
        try:
            pub_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
        except Exception as e:
            continue
        if pub_date >= min_date:
            # Compute similarity
            similarity = cosine_similarity(query_embedding, article.get("vector", []))
            # Save similarity along with the article
            article["similarity"] = similarity
            filtered.append(article)

    # Sort filtered articles by similarity (descending)
    filtered.sort(key=lambda a: a["similarity"], reverse=True)
    
    # Return top X results
    return filtered[:top_x]

#############################################
# MAIN EXECUTION
#############################################
if __name__ == "__main__":
    # STEP 1: Upload JSON file to storage (provide your file path)
    json_file_path = "articles.json"  # Ensure this file exists and follows your provided schema.
    file_uri = upload_json_to_storage(json_file_path)

    # STEP 2: Register the file on-chain
    register_file_on_chain(file_uri)

    # STEP 3: Semantic search demo:
    # Example query embedding (replace with your actual vector)
    query_embedding = [0.01] * 200  # Example: a dummy vector of 200 dimensions
    # Set a minimum publication date (ISO format, adjust as needed)
    min_pub_date = "2025-04-01T00:00:00+00:00"
    # Number of articles to return
    top_x = 3
    # Run semantic search
    top_articles = semantic_search(query_embedding, min_pub_date, top_x, json_file_path)
    
    print("\nTop matching articles:")
    for idx, article in enumerate(top_articles, start=1):
        print(f"Result {idx}:")
        print("  Web URL:", article.get("web_url"))
        print("  Pub Date:", article.get("metadata", {}).get("pub_date"))
        print("  Similarity:", article.get("similarity"))
        print("  Title:", article.get("metadata", {}).get("title", {}).get("main"))