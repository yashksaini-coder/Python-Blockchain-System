from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import binascii
import Crypto
import Crypto.Random
from Crypto.PublicKey import RSA
from uuid import uuid4

from blockchain.blockchain import Blockchain, MINING_REWARD, MINING_SENDER
from client.transaction import Transaction

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Define blockchain variables
blockchain = Blockchain()
node_identifier = str(uuid4()).replace("-", "")

# Main routes
@app.route("/")
def index():
    return render_template("index.html")

# Blockchain routes
@app.route("/blockchain")
def blockchain_index():
    return render_template("blockchain/index.html")

@app.route("/blockchain/configure")
def configure():
    return render_template("blockchain/configure.html")

@app.route("/blockchain/transactions/new", methods=["POST"])
def new_transaction():
    values = request.form

    required = ["sender_address", "recipient_address", "amount", "signature"]
    if not all(k in values for k in required):
        return "Missing values", 400

    transaction_result = blockchain.submit_transaction(
        values["sender_address"],
        values["recipient_address"],
        values["amount"],
        values["signature"],
    )

    if not transaction_result:
        response = {"message": "Invalid Transaction!"}
        return jsonify(response), 406
    else:
        response = {
            "message": "Transaction will be added to Block " + str(transaction_result)
        }
        return jsonify(response), 201

@app.route("/blockchain/transactions/get", methods=["GET"])
def get_transactions():
    transactions = blockchain.transactions

    response = {"transactions": transactions}
    return jsonify(response), 200

@app.route("/blockchain/chain", methods=["GET"])
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route("/blockchain/mine", methods=["GET"])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.chain[-1]
    nonce = blockchain.proof_of_work()

    # We must receive a reward for finding the proof.
    blockchain.submit_transaction(
        sender_address=MINING_SENDER,
        recipient_address=blockchain.node_id,
        value=MINING_REWARD,
        signature="",
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(nonce, previous_hash)

    response = {
        "message": "New Block Forged",
        "block_number": block["index"],
        "transactions": block["transactions"],
        "nonce": block["nonce"],
        "previous_hash": block["previous_hash"],
    }
    return jsonify(response), 200

@app.route("/blockchain/nodes/register", methods=["POST"])
def register_nodes():
    values = request.form
    nodes = values.get("nodes").replace(" ", "").split(",")

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        "message": "New nodes have been added",
        "total_nodes": [node for node in blockchain.nodes],
    }
    return jsonify(response), 201

@app.route("/blockchain/nodes/resolve", methods=["GET"])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {"message": "Our chain was replaced", "new_chain": blockchain.chain}
    else:
        response = {"message": "Our chain is authoritative", "chain": blockchain.chain}
    return jsonify(response), 200

@app.route("/blockchain/nodes/get", methods=["GET"])
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {"nodes": nodes}
    return jsonify(response), 200

# Client routes
@app.route("/client")
def client_index():
    return render_template("client/index.html")

@app.route("/client/make/transaction")
def make_transaction():
    return render_template("client/make_transaction.html")

@app.route("/client/view/transactions")
def view_transaction():
    return render_template("client/view_transactions.html")

@app.route("/client/wallet/new", methods=["GET"])
def new_wallet():
    random_gen = Crypto.Random.new().read
    private_key = RSA.generate(1024, random_gen)
    public_key = private_key.publickey()
    response = {
        "private_key": binascii.hexlify(private_key.exportKey(format="DER")).decode(
            "ascii"
        ),
        "public_key": binascii.hexlify(public_key.exportKey(format="DER")).decode(
            "ascii"
        ),
    }

    return jsonify(response), 200

@app.route("/client/generate/transaction", methods=["POST"])
def generate_transaction():
    sender_address = request.form["sender_address"]
    sender_private_key = request.form["sender_private_key"]
    recipient_address = request.form["recipient_address"]
    value = request.form["amount"]

    transaction = Transaction(
        sender_address, sender_private_key, recipient_address, value
    )

    response = {
        "transaction": transaction.to_dict(),
        "signature": transaction.sign_transaction(),
    }

    return jsonify(response), 200

def run_app(host='0.0.0.0', port=5000, debug=True):
    """Run the Flask application with the specified parameters"""
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('--host', default='0.0.0.0', type=str, help='host to listen on')
    args = parser.parse_args()
    
    run_app(host=args.host, port=args.port) 