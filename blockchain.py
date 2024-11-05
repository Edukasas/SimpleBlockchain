import concurrent.futures
import random
import time
import uuid
from datetime import datetime

from blockchain2.customhash import custom_hash


class UTXO:
    def __init__(self, tx_id, amount, owner):
        self.tx_id = tx_id
        self.amount = amount
        self.owner = owner

    def __repr__(self):
        return f"UTXO(tx_id={self.tx_id}, amount={self.amount}, owner={self.owner})"


class Transaction:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.tx_id = self.calculate_hash()

    def calculate_hash(self):
        tx_data = f"{[utxo.tx_id for utxo in self.inputs]}{[utxo.amount for utxo in self.outputs]}"
        return custom_hash(tx_data)

    def print_transaction(self):
        print(f"Transaction ID: {self.tx_id}")
        print("Inputs:")
        for utxo in self.inputs:
            print(f"  - {utxo}")
        print("Outputs:")
        for utxo in self.outputs:
            print(f"  - {utxo}")


class Block:
    def __init__(self, prev_hash, transactions, difficulty):
        self.prev_hash = prev_hash
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transactions = transactions
        self.merkle_root = self.calculate_merkle_root()
        self.nonce = 0
        self.difficulty = difficulty
        self.block_hash = None

    def calculate_merkle_root(self):
        tx_ids = [tx.tx_id for tx in self.transactions]
        if len(tx_ids) == 0:
            return None
        while len(tx_ids) > 1:
            if len(tx_ids) % 2 != 0:
                tx_ids.append(tx_ids[-1])
            new_level = []
            for i in range(0, len(tx_ids), 2):
                combined = tx_ids[i] + tx_ids[i + 1]
                new_level.append(custom_hash(combined.encode()))
            tx_ids = new_level
        return tx_ids[0]

    def calculate_hash(self):
        block_data = f"{self.prev_hash}{self.timestamp}{self.merkle_root}{self.nonce}{self.difficulty}"
        return custom_hash(block_data.encode())


class Blockchain:

    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.utxo_pool = {}
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def update_utxo_pool(self, transactions):
        for tx in transactions:
            for utxo in tx.inputs:
                if utxo.tx_id in self.utxo_pool:
                    del self.utxo_pool[utxo.tx_id]
            for utxo in tx.outputs:
                self.utxo_pool[utxo.tx_id] = utxo

    def create_genesis_block(self):
        genesis_utxo = UTXO("genesis_tx", 1000000, "genesis_owner")
        genesis_tx = Transaction([], [genesis_utxo])
        self.utxo_pool[genesis_utxo.tx_id] = genesis_utxo
        return Block("0", [genesis_tx], self.difficulty)

    def add_block(self, transactions):
        prev_hash = self.chain[-1].block_hash
        new_block = Block(prev_hash, transactions, self.difficulty)
        self.chain.append(new_block)
        for tx in transactions:
            for utxo in tx.inputs:
                if utxo.tx_id in self.utxo_pool:
                    del self.utxo_pool[utxo.tx_id]
            for utxo in tx.outputs:
                self.utxo_pool[utxo.tx_id] = utxo

    def verify_balance(self, transaction):
        total_input = sum(utxo.amount for utxo in transaction.inputs if utxo.tx_id in self.utxo_pool)
        total_output = sum(utxo.amount for utxo in transaction.outputs)
        return total_input >= total_output

    def add_transaction(self, transaction):
        if all(utxo.tx_id in self.utxo_pool for utxo in transaction.inputs) and self.verify_balance(transaction):
            self.pending_transactions.append(transaction)

    def mine_block_concurrently(self, candidate_block):
        timeout = 5
        max_trials = 100000
        start_time = time.time()
        trials = 0
        increase_factor = 1.5

        while True:
            while (time.time() - start_time) < timeout and trials < max_trials:
                candidate_block.block_hash = candidate_block.calculate_hash()
                if candidate_block.block_hash.startswith("0" * self.difficulty):
                    return candidate_block
                candidate_block.nonce += 1
                trials += 1
            print(
                f"Still mining... Increasing timeout to {timeout * increase_factor:.2f} seconds and max trials to {max_trials * increase_factor:.0f}.")

            timeout *= increase_factor
            max_trials = int(max_trials * increase_factor)

            trials = 0

    def mine_pending_transactions_concurrently(self):
        candidate_blocks = [self.create_candidate_block() for _ in range(5)]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.mine_block_concurrently, candidate_blocks)
            for result in results:
                if result:
                    self.chain.append(result)
                    self.update_utxo_pool(result.transactions)
                    self.pending_transactions = self.pending_transactions[100:]
                    return

    def create_candidate_block(self):
        transactions_to_mine = random.sample(self.pending_transactions, 100)
        prev_hash = self.chain[-1].block_hash
        return Block(prev_hash, transactions_to_mine, self.difficulty)

    def print_block(self, block_index):
        if 0 <= block_index < len(self.chain):
            block = self.chain[block_index]
            print(f"Block Index: {block_index}")
            print(f"Block Hash: {block.block_hash}")
            print(f"Previous Hash: {block.prev_hash}")
            print(f"Merkle Root: {block.merkle_root}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Transactions: {len(block.transactions)}")
        else:
            print("Block index out of range.")


def generate_users(blockchain, num_users):
    users = []
    for i in range(num_users):
        name = f"User{i}"
        public_key = custom_hash(name.encode())
        user = User(name, public_key, [])

        balance = random.randint(100, 1000000)

        initial_utxo = UTXO(f"utxo_{uuid.uuid4()}", balance, user.public_key)

        user.utxos.append(initial_utxo)
        blockchain.utxo_pool[initial_utxo.tx_id] = initial_utxo

        users.append(user)
    return users


class User:
    def __init__(self, name, public_key, utxos):
        self.name = name
        self.public_key = public_key
        self.utxos = utxos

    def balance(self):
        return sum(utxo.amount for utxo in self.utxos)


def generate_transactions(users, target_num_transactions):
    transactions = []

    while len(transactions) < target_num_transactions:
        sender = random.choice(users)

        if sender.utxos:
            utxo_to_spend = random.choice(sender.utxos)

            amount_to_send = random.randint(1, utxo_to_spend.amount)

            receiver = random.choice([user for user in users if user != sender])

            receiver_utxo = UTXO(uuid.uuid4(), amount_to_send, receiver.public_key)
            change_utxo = None

            if utxo_to_spend.amount > amount_to_send:
                change_utxo = UTXO(uuid.uuid4(), utxo_to_spend.amount - amount_to_send,
                                   sender.public_key)

            new_tx = Transaction([utxo_to_spend], [receiver_utxo] + ([change_utxo] if change_utxo else []))

            if all(utxo.tx_id in blockchain.utxo_pool for utxo in new_tx.inputs):
                transactions.append(new_tx)

                sender.utxos.remove(utxo_to_spend)
                if change_utxo:
                    sender.utxos.append(change_utxo)
                receiver.utxos.append(receiver_utxo)

    return transactions


if __name__ == "__main__":
    blockchain = Blockchain(difficulty=0)
    users = generate_users(blockchain, 1000)

    print(f"Total Users Created: {len(users)}")

    transactions = generate_transactions(users, 1000)

    print(f"Total Transactions Created: {len(transactions)}")
    for tx in transactions:
        blockchain.add_transaction(tx)

    while len(blockchain.pending_transactions) > 0:
        blockchain.mine_pending_transactions_concurrently()

    latest_block_index = len(blockchain.chain) - 1
    blockchain.print_block(latest_block_index)

    latest_block = blockchain.chain[latest_block_index]
    print(f"Transactions in Block {latest_block_index}:")
    for transaction in latest_block.transactions:
        transaction.print_transaction()
