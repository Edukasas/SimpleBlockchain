# Blockchain Simulation

This project simulates a simple blockchain using Python. The code supports basic blockchain features, including UTXOs (unspent transaction outputs), transactions, block mining, and a user-defined difficulty level for mining.

## Table of Contents
- [Installation](#installation)
- [Overview](#overview)
- [Usage](#usage)
  - [Generate Users and Initial UTXOs](#generate-users-and-initial-utxos)
  - [Add Transactions](#add-transactions)
  - [Mine Pending Transactions](#mine-pending-transactions)
  - [Print Specific Transactions and Blocks](#print-specific-transactions-and-blocks)
- [Functions](#functions)
  - [print_transaction](#print_transaction)
  - [print_block](#print_block)

## Installation
1. Clone or download this repository.
2. Ensure Python 3.x is installed on your machine.
3. Install any necessary libraries. This code requires only the standard library and a custom hashing function in `blockchain2.customhash`, so ensure it’s available in the specified path.

## Overview
This blockchain simulation has the following classes:

- **UTXO**: Represents an unspent transaction output, keeping track of transaction ID, amount, and owner.
- **Transaction**: Holds inputs and outputs for a transaction and generates a unique transaction ID.
- **Block**: Holds transactions, performs proof-of-work mining, and calculates its hash based on the previous block.
- **Blockchain**: Manages the chain of blocks, pending transactions, UTXO pool, and difficulty settings.
- **User**: Represents a user with a public key and associated UTXOs.

## Usage
The blockchain allows you to:

- Generate users with initial UTXOs.
- Add transactions between users.
- Mine pending transactions to add them to a block in the blockchain.
- Print transaction and block details for verification and exploration.

### Generate Users and Initial UTXOs
In the main function, `generate_users(blockchain, num_users)` creates user objects with a unique public key and adds initial UTXOs to the `utxo_pool` for each user.

### Add Transactions
Use the `generate_transactions(users, num_transactions)` function to generate transactions between users, with random amounts based on available UTXOs.

Each transaction is added to the blockchain using `blockchain.add_transaction(transaction)`. Only transactions with valid UTXOs are added to the list of pending transactions.

### Mine Pending Transactions
To process and secure the pending transactions in a new block, call:

    blockchain.mine_pending_transactions()
    
Each mined block is appended to the chain, and the pending transactions are cleared.

### Print Specific Transactions and Blocks
  The <b>print_transaction</b> function in <b>Transaction</b> and <b>print_block</b> function in <b>Blockchain</b> allow you to view details of any specific transaction or block.
## Functions

### print_transaction

Usage: Prints the details of a transaction, including its ID, inputs, and outputs.

    # To print the first transaction in the first block
    blockchain.chain[0].transactions[0].print_transaction()

### print_block
Usage: Prints details of a specified block, including its hash, previous hash, merkle root, timestamp, and all transactions contained within it.

    # To print the first block in the blockchain
    blockchain.print_block(0)
