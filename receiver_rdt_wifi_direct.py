import socket
import json
import webbrowser
import struct
import os
import time
from cryptography.fernet import Fernet
from ytmusicapi import YTMusic

# Constants
PORT = 12345
CHUNK_SIZE = 1024

# Get sender IP & save path
SENDER_IP = input("Enter sender IP Address: ").strip()
save_path = input("Enter save path (.json file): ").strip()

# Load encryption key securely
key_file_path = "encryption_key.key"
if not os.path.exists(key_file_path):
    print("Error: Encryption key file not found!")
    exit(1)

with open(key_file_path, "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key)

# Connect to sender
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SENDER_IP, PORT))
    print("Connected to sender, receiving encrypted playlist...")
except Exception as e:
    print(f"Connection failed: {e}")
    exit(1)

# Reliable Data Transfer (RDT) with Acknowledgments
encrypted_data = b""
expected_seq = 0

try:
    while True:
        packet = client_socket.recv(CHUNK_SIZE + 4)  # First 4 bytes → sequence number
        if not packet:
            break

        seq_num = struct.unpack("!I", packet[:4])[0]  # Extract sequence number
        data = packet[4:]  # Extract data

        if seq_num == expected_seq:
            encrypted_data += data
            ack_packet = struct.pack("!I", seq_num)
            client_socket.send(ack_packet)
            expected_seq += 1
        else:
            print(f"Out-of-order packet {seq_num}, expected {expected_seq}. Ignoring...")

except Exception as e:
    print(f"Error during data transfer: {e}")
finally:
    print("Closing connection...")
    client_socket.close()  # Ensure socket is properly closed

print("Playlist received successfully!")

# Decrypt Playlist Data
try:
    decrypted_data = cipher.decrypt(encrypted_data)
    print("File decrypted successfully!")
except Exception as e:
    print(f"Error decrypting file: {e}")
    exit(1)

# Save and Parse JSON
try:
    with open(save_path, "wb") as file:
        file.write(decrypted_data)
    print(f"Playlist saved at: {save_path}")

    # Load JSON data
    with open(save_path, "r", encoding="utf-8") as json_file:
        playlist_data = json.load(json_file)

    print(f"Playlist Name: {playlist_data['name']}")
    print("Songs in Playlist:")
    for track in playlist_data["tracks"]:
        print(f"{track['name']} - {track['artist']} - ({track['album']})")

except Exception as e:
    print(f"Error processing JSON file: {e}")

# Reconnect to Internet After Wi-Fi Direct
def reconnect_wifi():
    HOME_WIFI_SSID = "sandeeplathi_5G"  # Change this to your actual Wi-Fi name

    print("\nReconnecting to internet...")
    time.sleep(2)

    if os.name == "nt":
        os.system("netsh wlan disconnect")
        time.sleep(3)
        os.system(f'netsh wlan connect name="{HOME_WIFI_SSID}"')

    print(f"Reconnected to {HOME_WIFI_SSID} successfully!\n")

# Call the reconnect function
reconnect_wifi()

# Ask User for Platform Selection
print("\nWhere would you like to import the playlist?")
print("1. Spotify")
print("2. Apple Music (Manual)")
print("3. YouTube Music")

choice = input("Enter choice: ").strip()

# Automate YouTube Music Playlist Creation
if choice == "3":
    try:
        print("\nCreating YouTube Music playlist...")
        yt = YTMusic("headers_auth.json")  # Load authentication headers

        # Ensure playlist name is a valid string
        playlist_name = playlist_data.get("name", "Unnamed Playlist")  # Default if None
        playlist_name = f"{playlist_name} (Shared)"  # Safe concatenation

        playlist_desc = "Playlist imported via Wi-Fi Direct"
        playlist_id = yt.create_playlist(playlist_name, playlist_desc, privacy_status="PUBLIC")

        print(f"Playlist '{playlist_name}' created successfully!")
        print(f"Open your playlist: https://music.youtube.com/playlist?list={playlist_id}")

        # Add songs to YouTube Music Playlist
        video_ids = []
        for song in playlist_data.get("tracks", []):  # Ensure tracks exist
            youtube_music_id = song.get("youtube_music_id")  # Avoid NoneType error
            if isinstance(youtube_music_id, str) and "v=" in youtube_music_id:  # Ensure it's a valid URL
                video_id = youtube_music_id.split("v=")[-1]  # Extract video ID
                video_ids.append(video_id)

        if video_ids:
            yt.add_playlist_items(playlist_id, video_ids)
            print("Songs added successfully!")
        else:
            print("No valid YouTube Music songs found.")

    except Exception as e:
        print(f"Error creating YouTube Music playlist: {e}")

# Open links for Spotify or Apple Music
elif choice == "1":
    for song in playlist_data.get("tracks", []):  # Ensure tracks exist
        spotify_id = song.get("spotify_id")
        if isinstance(spotify_id, str):  # Ensure it's a valid URL
            webbrowser.open(spotify_id)
elif choice == "2":
    for song in playlist_data.get("tracks", []):  # Ensure tracks exist
        apple_music_id = song.get("apple_music_id")
        if isinstance(apple_music_id, str):  # Ensure it's a valid URL
            webbrowser.open(apple_music_id)
else:
    print("Invalid choice. No songs will be imported.")
