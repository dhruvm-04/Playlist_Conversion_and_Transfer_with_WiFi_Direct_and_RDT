import socket
import json
import webbrowser
import struct
import os
from cryptography.fernet import Fernet
from ytmusicapi import YTMusic

# Constants
PORT = 12345
CHUNK_SIZE = 1024

# Get sender IP & save path
SENDER_IP = input("Enter sender IP Address: ").strip()
save_path = input("Enter save path (.json file): ").strip()
if not save_path.endswith('.json'):
    save_path += '.json'

# Load encryption key
key_file_path = "encryption_key.key"
if not os.path.exists(key_file_path):
    print("Error: Encryption key file not found!")
    exit(1)

try:
    with open(key_file_path, "rb") as key_file:
        key = key_file.read()
    cipher = Fernet(key)
except Exception as e:
    print(f"Error loading encryption key: {e}")
    exit(1)

# Connect to sender
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(10)
    client_socket.connect((SENDER_IP, PORT))
    print("Connected to sender, receiving encrypted playlist...")
except Exception as e:
    print(f"Connection failed: {e}")
    exit(1)

# Receive data with acknowledgments
encrypted_data = b""
expected_seq = 0

try:
    client_socket.settimeout(30)
    while True:
        try:
            packet = client_socket.recv(CHUNK_SIZE + 4)
            if not packet:
                break

            seq_num = struct.unpack("!I", packet[:4])[0]
            data = packet[4:]

            if seq_num == expected_seq:
                encrypted_data += data
                ack_packet = struct.pack("!I", seq_num)
                client_socket.send(ack_packet)
                expected_seq += 1
            else:
                print(f"Out-of-order packet {seq_num}, expected {expected_seq}")
        except socket.timeout:
            break

    # Send final ACK
    try:
        print("Sending final acknowledgment...")
        client_socket.send(b"DONE")
        
        # Wait for sender confirmation
        client_socket.settimeout(10)
        confirmation = client_socket.recv(1024)
        if confirmation == b"CLOSING":
            print("Sender confirmed closure.")
    except Exception as e:
        print(f"Error during final handshake: {e}")

except Exception as e:
    print(f"Error during data transfer: {e}")
finally:
    client_socket.close()

if not encrypted_data:
    print("Error: No data received!")
    exit(1)

print("Playlist received successfully!")

# Decrypt and save data
try:
    decrypted_data = cipher.decrypt(encrypted_data)
    with open(save_path, "wb") as file:
        file.write(decrypted_data)
    print(f"Playlist saved at: {save_path}")

    # Parse JSON
    with open(save_path, "r", encoding="utf-8") as json_file:
        playlist_data = json.load(json_file)

    # Handle playlist name safely
    playlist_name = "Unnamed Playlist"
    if "name" in playlist_data and isinstance(playlist_data["name"], str):
        playlist_name = playlist_data["name"]
    
    print(f"Playlist Name: {playlist_name}")
    
    print("Songs in Playlist:")
    for track in playlist_data.get("tracks", []):
        if isinstance(track, dict):
            print(f"{track.get('name', 'Unknown')} - {track.get('artist', 'Unknown')}")

except Exception as e:
    print(f"Error processing file: {e}")
    exit(1)

# Platform selection
print("\nWhere would you like to import the playlist?")
print("1. Spotify\n2. Apple Music\n3. YouTube Music")
choice = input("Enter choice (1-3): ").strip()

# YouTube Music integration
if choice == "3":
    try:
        print("\nCreating YouTube Music playlist...")
        
        # Safe playlist name handling
        yt_playlist_name = "Shared Playlist"  # Default name
        if playlist_name and isinstance(playlist_name, str):
            yt_playlist_name = f"{playlist_name} (Shared)"
            
        try:
            yt = YTMusic("headers_auth.json")
            playlist_id = yt.create_playlist(
                yt_playlist_name, 
                "Playlist imported via Wi-Fi Direct", "PUBLIC"
            )
            print(f"Playlist '{yt_playlist_name}' created!")
            
            # Add songs
            video_ids = []
            for song in playlist_data.get("tracks", []):
                if not isinstance(song, dict):
                    continue
                    
                yt_id = song.get("youtube_music_id", "")
                if isinstance(yt_id, str) and "v=" in yt_id:
                    video_id = yt_id.split("v=")[-1].split("&")[0]
                    video_ids.append(video_id)
            
            if video_ids:
                yt.add_playlist_items(playlist_id, video_ids)
                print(f"Added {len(video_ids)} songs to YouTube Music")
                print(f"Open: https://music.youtube.com/playlist?list={playlist_id}")
            else:
                print("No valid YouTube Music songs found.")
                
        except Exception as e:
            print(f"YouTube Music error: {e}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")

# Handle other platforms
elif choice == "1":
    print("Opening Spotify links...")
    for song in playlist_data.get("tracks", []):
        if isinstance(song, dict) and isinstance(song.get("spotify_id"), str):
            webbrowser.open(song["spotify_id"])
elif choice == "2":
    print("Opening Apple Music links...")
    for song in playlist_data.get("tracks", []):
        if isinstance(song, dict) and isinstance(song.get("apple_music_id"), str):
            webbrowser.open(song["apple_music_id"])
