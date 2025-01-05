#!/usr/bin/python3

import zlib
import sys

def calculate_crc32(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            crc32_value = zlib.crc32(data) & 0xFFFFFFFF
            print(f"{crc32_value:08x}")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 crc32.py <file_path>")
    else:
        calculate_crc32(sys.argv[1])
