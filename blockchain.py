import hashlib
import random


class User:
    def __init__(self, name, public_key, balance):
        self.name = name
        self.public_key = public_key
        self.balance = balance

    def __str__(self):
        return f"I'm {self.name}, key {self.public_key}, {self.balance} balance"


def generate_users(num_users):
    users = []
    for i in range(num_users):
        name = f"User{i}"
        public_key = hashlib.sha256(name.encode()).hexdigest()
        balance = random.randint(100, 1000000)
        users.append(User(name, public_key, balance))
    return users


if __name__ == "__main__":
    users = generate_users(10)
    for user in users:
        print(user)
