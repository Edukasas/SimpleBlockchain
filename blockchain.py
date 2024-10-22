import hashlib
import random
import time


class User:
    def __init__(self, name, public_key, balance):
        self.name = name
        self.public_key = public_key
        self.balance = balance


class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.tx_id = self.calculate_hash()

    def calculate_hash(self):
        tx_data = f"{self.sender}{self.receiver}{self.amount}"
        return hashlib.sha256(tx_data.encode()).hexdigest()


class Block:
    def __init__(self, prev_hash, transactions, difficulty):
        self.prev_hash = prev_hash
        self.timestamp = time.time()
        self.transactions = transactions
        self.merkle_root = self.calculate_merkle_root()
        self.nonce = 0
        self.difficulty = difficulty
        self.block_hash = self.mine_block()

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
                new_level.append(hashlib.sha256(combined.encode()).hexdigest())
            tx_ids = new_level
        return tx_ids[0]

    def calculate_hash(self):
        block_data = f"{self.prev_hash}{self.timestamp}{self.merkle_root}{self.nonce}{self.difficulty}"
        return hashlib.sha256(block_data.encode()).hexdigest()

    def mine_block(self):
        target = "0" * self.difficulty
        while True:
            block_hash = self.calculate_hash()
            if block_hash.startswith(target):
                return block_hash
            self.nonce += 1


class Blockchain:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self):
        return Block("0", [], self.difficulty)

    def add_block(self, transactions):
        prev_hash = self.chain[-1].block_hash
        new_block = Block(prev_hash, transactions, self.difficulty)
        self.chain.append(new_block)

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self):
        if len(self.pending_transactions) < 100:
            return
        selected_transactions = random.sample(self.pending_transactions, 100)
        self.add_block(selected_transactions)
        for tx in selected_transactions:
            self.pending_transactions.remove(tx)


def generate_users(num_users):
    users = []
    for i in range(num_users):
        name = f"User{i}"
        public_key = hashlib.sha256(name.encode()).hexdigest()
        balance = random.randint(100, 1000000)
        users.append(User(name, public_key, balance))
    return users


def generate_transactions(users, num_transactions):
    transactions = []
    for _ in range(num_transactions):
        sender = random.choice(users)
        receiver = random.choice([user for user in users if user != sender])
        amount = random.randint(1, sender.balance)
        transactions.append(Transaction(sender.public_key, receiver.public_key, amount))
    return transactions


# Main logic
if __name__ == "__main__":
    users = generate_users(1000)

    transactions = generate_transactions(users, 10000)

    blockchain = Blockchain(difficulty=4)

    for tx in transactions:
        blockchain.add_transaction(tx)

    while len(blockchain.pending_transactions) > 0:
        blockchain.mine_pending_transactions()

    for idx, block in enumerate(blockchain.chain):
        print(f"Block {idx} - Hash: {block.block_hash}, Previous Hash: {block.prev_hash}")
