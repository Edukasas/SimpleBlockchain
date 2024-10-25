import random
import time


# Utility functions
def int_to_hex(byte):
    return f"{byte:02x}"


def swap4bits(byte):
    first4 = (byte >> 4) & 0x0F
    last4 = byte & 0x0F
    return (last4 << 4) | first4


def generate_salt(length=16):
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    random.seed(time.time())
    return ''.join(random.choice(chars) for _ in range(length))


def custom_hash(input_string):
    if isinstance(input_string, bytes):
        input_string = input_string.decode('utf-8')

    hashes = [
        0xFA153BE9AB2842EA,
        0xBABABABA01032587,
        0xC0DE15500DAFFAE7
    ]
    prime = 0x10E93214
    salt = generate_salt()
    salted_input = salt + input_string

    for c in salted_input:
        byte_val = ord(c)
        swapped = swap4bits(byte_val)

        for i in range(len(hashes)):
            hashes[i] ^= swapped * prime
            hashes[i] = (hashes[i] * 0x5BD1E995) ^ (hashes[i] >> (i + 1))
            hashes[i] = ((hashes[i] << (5 + i)) & 0xFFFFFFFFFFFFFFFF) | (hashes[i] >> (64 - (5 + i)))

    # Final transformation step
    for i in range(len(hashes)):
        hashes[i] ^= (hashes[(i + 1) % len(hashes)] * prime) ^ (hashes[i] >> 31)
        hashes[i] = (hashes[i] * 0x5BD1E995) ^ (hashes[i] >> 33)

    # Concatenate hex representations of hashes
    result = ''.join(f"{x:016x}" for x in hashes)
    return salt + result
