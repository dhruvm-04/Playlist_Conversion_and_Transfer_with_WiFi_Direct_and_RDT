import socket
import os
import struct
from cryptography.fernet import Fernet

# Constants
PORT = 12345
CHUNK_SIZE = 1024

# Get Receiver IP & Playlist Path
RECEIVER_IP = input("Enter receiver IP Address: ").strip()
playlist_path = input("Enter path to the playlist JSON file: ").strip()

if not os.path.exists(playlist_path):
    print(f"Error: File not found at {playlist_path}")
    exit(1)

# Load or Generate Encryption Key
key_file_path = "encryption_key.key"
try:
    if not os.path.exists(key_file_path):
        print("Generating new encryption key...")
        key = Fernet.generate_key()
        with open(key_file_path, "wb") as key_file:
            key_file.write(key)
    else:
        with open(key_file_path, "rb") as key_file:
            key = key_file.read()
    
    cipher = Fernet(key)
except Exception as e:
    print(f"Error with encryption key: {e}")
    exit(1)

# Read and Encrypt Playlist
try:
    with open(playlist_path, "rb") as file:
        plaintext = file.read()
    encrypted_data = cipher.encrypt(plaintext)
    print(f"Playlist encrypted: {len(encrypted_data)} bytes")
except Exception as e:
    print(f"Error encrypting file: {e}")
    exit(1)

# Setup Socket
try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(1)
    print(f"Waiting for connection on port {PORT}...")
except Exception as e:
    print(f"Socket error: {e}")
    exit(1)

try:
    conn, addr = server_socket.accept()
    print(f"Connected to {addr}")
    
    # Send data chunks
    total_packets = (len(encrypted_data) + CHUNK_SIZE - 1) // CHUNK_SIZE
    print(f"Sending {total_packets} packets...")
    
    for seq_num in range(total_packets):
        chunk = encrypted_data[seq_num * CHUNK_SIZE:(seq_num + 1) * CHUNK_SIZE]
        packet = struct.pack("!I", seq_num) + chunk
        conn.sendall(packet)
        
        # Wait for ACK
        try:
            ack = conn.recv(4)
            if not ack:
                print("Connection closed unexpectedly")
                break
                
            recv_seq = struct.unpack("!I", ack)[0]
            if recv_seq == seq_num:
                print(f"Packet {seq_num+1}/{total_packets} confirmed", end="\r")
            else:
                print(f"Unexpected ACK {recv_seq}, expected {seq_num}")
        except Exception as e:
            print(f"ACK error: {e}")
            break
    
    print("\nWaiting for final acknowledgment...")
    
    # Wait for final ACK with improved timeout
    conn.settimeout(15)  # Longer timeout for final ACK
    try:
        final_ack = conn.recv(1024)
        if final_ack == b"DONE":
            print("Final ACK received, sending closure confirmation...")
            conn.sendall(b"CLOSING")
        else:
            print(f"Unexpected final message: {final_ack}")
    except socket.timeout:
        print("Timeout waiting for final ACK")
    
except Exception as e:
    print(f"Transfer error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
    server_socket.close()
    print("Connection closed")
