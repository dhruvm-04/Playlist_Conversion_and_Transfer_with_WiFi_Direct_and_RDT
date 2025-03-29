import socket
import os
import struct
import time
import hashlib
from cryptography.fernet import Fernet

# Constants
PORT = 12345
CHUNK_SIZE = 1024
WINDOW_SIZE = 4  # Selective Repeat Window Size
TIMEOUT = 5


def compute_checksum(data):
    return hashlib.sha256(data).hexdigest().encode()


def load_or_generate_key():
    key_file_path = "encryption_key.key"
    if not os.path.exists(key_file_path):
        key = Fernet.generate_key()
        with open(key_file_path, "wb") as key_file:
            key_file.write(key)
    else:
        with open(key_file_path, "rb") as key_file:
            key = key_file.read()
    return Fernet(key)


def send_playlist():
    receiver_ip = input("Enter receiver IP Address: ").strip()
    playlist_path = input("Enter path to the playlist JSON file: ").strip()

    if not os.path.exists(playlist_path):
        print(f"Error: File not found at {playlist_path}")
        return

    cipher = load_or_generate_key()
    with open(playlist_path, "rb") as file:
        plaintext = file.read()
    encrypted_data = cipher.encrypt(plaintext)
    checksum = compute_checksum(encrypted_data)

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", PORT))
        server_socket.listen(1)
        print(f"Waiting for receiver connection on port {PORT}...")

        conn, addr = server_socket.accept()
        print(f"Connected to receiver {addr}")

        total_packets = (len(encrypted_data) + CHUNK_SIZE - 1) // CHUNK_SIZE
        conn.sendall(checksum)

        base = 0
        window = {}
        acked_packets = set()

        while base < total_packets:
            for seq_num in range(base, min(base + WINDOW_SIZE, total_packets)):
                if seq_num not in window and seq_num not in acked_packets:
                    chunk = encrypted_data[seq_num * CHUNK_SIZE:(seq_num + 1) * CHUNK_SIZE]
                    packet = struct.pack("!I", seq_num) + chunk
                    conn.sendall(packet)
                    window[seq_num] = time.time()

            conn.settimeout(TIMEOUT)
            try:
                ack = conn.recv(4)
                if ack:
                    recv_seq = struct.unpack("!I", ack)[0]
                    if recv_seq in window:
                        del window[recv_seq]
                        acked_packets.add(recv_seq)

                    while base in acked_packets:
                        base += 1

            except socket.timeout:
                for seq_num in list(window.keys()):
                    if seq_num not in acked_packets:
                        chunk = encrypted_data[seq_num * CHUNK_SIZE:(seq_num + 1) * CHUNK_SIZE]
                        packet = struct.pack("!I", seq_num) + chunk
                        conn.sendall(packet)
                        window[seq_num] = time.time()

        while len(acked_packets) < total_packets:
            ack = conn.recv(4)
            if ack:
                recv_seq = struct.unpack("!I", ack)[0]
                acked_packets.add(recv_seq)

        conn.sendall(b"DONE")
        time.sleep(1)
        conn.close()
    except Exception as e:
        print(f"Error in sending: {e}")


def receive_playlist():
    sender_ip = input("Enter sender IP Address: ").strip()
    save_path = input("Enter save path for received JSON file: ").strip()
    if not save_path.endswith('.json'):
        save_path += '.json'

    cipher = load_or_generate_key()
    encrypted_data = {}

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((sender_ip, PORT))
        print("Connected to sender. Receiving data...")

        received_checksum = client_socket.recv(64)
        print("Received checksum.")

        while True:
            packet = client_socket.recv(CHUNK_SIZE + 4)
            if not packet or packet == b"DONE":
                break
            
            seq_num = struct.unpack("!I", packet[:4])[0]
            data = packet[4:]
            
            if 0 <= seq_num < (10**6):  # Prevent invalid sequence numbers
                encrypted_data[seq_num] = data
                client_socket.sendall(struct.pack("!I", seq_num))
                print(f"Received and acknowledged packet {seq_num}")

        sorted_data = b"".join(encrypted_data[i] for i in sorted(encrypted_data.keys()))

        if compute_checksum(sorted_data) == received_checksum:
            with open(save_path, "wb") as file:
                file.write(cipher.decrypt(sorted_data))
            print(f"Playlist saved at: {save_path}, checksum verified.")
        else:
            print("Checksum mismatch! Possible data corruption.")

        client_socket.close()
    except Exception as e:
        print(f"Error in receiving: {e}")


if __name__ == "__main__":
    mode = input("Are you the sender or receiver? (s/r): ").strip().lower()
    if mode == "s":
        send_playlist()
    elif mode == "r":
        receive_playlist()
    else:
        print("Invalid choice. Please enter 's' for sender or 'r' for receiver.")