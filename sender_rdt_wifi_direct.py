import socket
import os
import struct
from cryptography.fernet import Fernet

# Constants
PORT = 12345
CHUNK_SIZE = 1024  # Packet size

# Get Receiver IP & Playlist Path
RECEIVER_IP = input("Enter receiver IP Address: ").strip()
playlist_path = input("Enter path to the playlist JSON file: ").strip()

# Load or Generate Encryption Key
key_file_path = "encryption_key.key"
if not os.path.exists(key_file_path):
    print("Encryption key not found! Generating new key...")
    key = Fernet.generate_key()
    with open(key_file_path, "wb") as key_file:
        key_file.write(key)
else:
    with open(key_file_path, "rb") as key_file:
        key = key_file.read()

cipher = Fernet(key)

# Read and Encrypt Playlist JSON
try:
    with open(playlist_path, "rb") as file:
        plaintext = file.read()
    encrypted_data = cipher.encrypt(plaintext)
    print("Playlist encrypted successfully!")
except Exception as e:
    print(f"Error encrypting playlist file: {e}")
    exit(1)

# Setup Sender Socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", PORT))
server_socket.listen(1)
print(f"Waiting for connection on port {PORT}...")

conn, addr = server_socket.accept()
print(f"Connected to {addr}")

# Send Encrypted Data with Reliable Data Transfer (RDT)
seq_num = 0
offset = 0

try:
    while offset < len(encrypted_data):
        chunk = encrypted_data[offset:offset + CHUNK_SIZE]
        packet = struct.pack("!I", seq_num) + chunk
        conn.sendall(packet)
        print(f"Sent packet {seq_num}")
        seq_num += 1
        offset += CHUNK_SIZE

    print("Encrypted playlist sent successfully!")

except Exception as e:
    print(f"Error during data transfer: {e}")

finally:
    print("Closing connection...")
    conn.close()
    server_socket.close()