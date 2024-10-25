import random
import time

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
                new_level.append(custom_hash(combined.encode()))
            tx_ids = new_level
        return tx_ids[0]

    def calculate_hash(self):
        block_data = f"{self.prev_hash}{self.timestamp}{self.merkle_root}{self.nonce}{self.difficulty}"
        return custom_hash(block_data.encode())

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
        self.utxo_pool = {}
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self):
        genesis_utxo = UTXO("genesis_tx", 1000000, "genesis_owner")
        genesis_tx = Transaction([], [genesis_utxo])
        self.utxo_pool[genesis_utxo.tx_id] = genesis_utxo  # UTXO pool is now initialized
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

    def add_transaction(self, transaction):
        if all(utxo.tx_id in self.utxo_pool for utxo in transaction.inputs):
            self.pending_transactions.append(transaction)

    def mine_pending_transactions(self):
        if len(self.pending_transactions) < 1:
            return
        self.add_block(self.pending_transactions[:])
        self.pending_transactions.clear()


def generate_users(num_users):
    users = []
    for i in range(num_users):
        name = f"User{i}"
        public_key = custom_hash(name.encode())
        users.append(User(name, public_key, []))
    return users


class User:
    def __init__(self, name, public_key, utxos):
        self.name = name
        self.public_key = public_key
        self.utxos = utxos

    def balance(self):
        return sum(utxo.amount for utxo in self.utxos)


def generate_transactions(users, num_transactions):
    transactions = []
    for _ in range(num_transactions):
        sender = random.choice(users)
        if sender.utxos:
            utxo_to_spend = random.choice(sender.utxos)
            receiver = random.choice([user for user in users if user != sender])
            amount_to_send = random.randint(1, utxo_to_spend.amount)

            receiver_utxo = UTXO(utxo_to_spend.tx_id, amount_to_send, receiver.public_key)
            change_utxo = None
            if utxo_to_spend.amount > amount_to_send:
                change_utxo = UTXO(utxo_to_spend.tx_id + "_change", utxo_to_spend.amount - amount_to_send, sender.public_key)

            new_tx = Transaction([utxo_to_spend], [receiver_utxo] + ([change_utxo] if change_utxo else []))

            sender.utxos.remove(utxo_to_spend)
            if change_utxo:
                sender.utxos.append(change_utxo)
            receiver.utxos.append(receiver_utxo)

            transactions.append(new_tx)

    return transactions


if __name__ == "__main__":
    users = generate_users(10)

    blockchain = Blockchain(difficulty=2)

    for user in users:
        initial_utxo = UTXO(f"init_{user.public_key[:6]}", random.randint(100, 1000), user.public_key)
        user.utxos.append(initial_utxo)
        blockchain.utxo_pool[initial_utxo.tx_id] = initial_utxo

    transactions = generate_transactions(users, 100)

    for tx in transactions:
        blockchain.add_transaction(tx)

    while len(blockchain.pending_transactions) > 0:
        blockchain.mine_pending_transactions()

    for idx, block in enumerate(blockchain.chain):
        print(f"Block {idx} - Hash: {block.block_hash}, Previous Hash: {block.prev_hash}")

    print("\nFinal UTXO Pool:")
    for utxo in blockchain.utxo_pool.values():
        print(utxo)
