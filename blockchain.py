import hashlib
import random


class User:
    def __init__(self, name, public_key, balance):
        self.name = name
        self.public_key = public_key
        self.balance = balance

    def __str__(self):
        return f"I'm {self.name}, key {self.public_key}, {self.balance} balance"


class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.tx_id = self.calculate_hash()

    def calculate_hash(self):
        tx_data = f"{self.sender}{self.receiver}{self.amount}"
        return hashlib.sha256(tx_data.encode()).hexdigest()

    def __str__(self):
        return f"Sender {self.sender}, Receiver {self.receiver}, amount {self.amount}, tx_id {self.tx_id}"


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


if __name__ == "__main__":
    users = generate_users(4)
    transactions = generate_transactions(users, 5)
    for transaction in transactions:
        print(transaction)
    for transaction in users:
        print(transaction)
