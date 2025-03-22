# Wi-Fi Direct Playlist Sharing - **ONGOING PROJECT**
A **Python** project based on the concepts of **Computer Networks** that enables **Spotify playlist sharing over Wi-Fi Direct with cross platform conversion options**.
It supports cross-platform playlist conversion, allowing users to fetch Spotify playlists and retrieve equivalent links for Apple Music & YouTube Music.
The system ensures **secure, reliable, and efficient** transfer using encryption and Reliable Data Transfer (RDT) mechanisms.

## Features
- Fetch Spotify playlists, extract song data & retrieve their links for **Apple Music & YouTube Music**, adding them to a json file for further usage.
- **Cryptography** to encrypt chunks before transmission, with an encryption key.
-  **Wi-Fi Direct connectivity** for sharing playlists among users, without internet access.
-  **End-to-end encryption** using the symmetric encryption of `cryptography.fernet` library of Python.
-  **Reliable Data Transfer (RDT)** with packet loss handling.
-  **Automated YouTube Music Playlist Creation** using the YouTube Music API to create playlists and add songs dynamically.

## Tools Used
- **Python**
  - **Spotipy** (Spotify API)
  - **ytmusicapi** (YouTube Music API)
  - **Cryptography** (Fernet) (AES-based encryption)
  - **PyWiFi** (Wi-Fi Direct setup)
- **Sockets & Struct** (Reliable data transfer & networks)

##  System Requirements
- Python 3.8+
- Supported on Windows, macOS, and Linux
- Requires a Wi-Fi Direct-compatible network adapter

## Future Improvements Planned
- Graphical User Interface (**GUI**)
- **Mobile** Compatibility


---
DISCLAIMER: THIS APP WILL **NOT** WORK FOR USERS **NOT WHITELISTED** ON GOOGLE CLOUD CONSOLE
PLEASE **SET UP YOUR GOOGLE CLOUD** CONSOLE APP BEFORE MOVING FORWARD
