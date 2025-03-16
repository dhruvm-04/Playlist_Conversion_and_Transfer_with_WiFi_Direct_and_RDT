import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import json

# Spotify API Credentials
SPOTIFY_CLIENT_ID = "your_cliend_id"
SPOTIFY_CLIENT_SECRET = "your_secret_id"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "playlist-read-private"

# Initialize Spotify Client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE))

# Function to Match Songs Across Platforms
def get_matching_song(spotify_url):
    # Fetch equivalent track links from Apple Music & YouTube Music using Odesli API.
    try:
        api_url = "https://api.song.link/v1-alpha.1/links"
        params = {"url": spotify_url, "userCountry": "US"}
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "apple_music_id": data.get("linksByPlatform", {}).get("appleMusic", {}).get("url", None),
                "youtube_music_id": data.get("linksByPlatform", {}).get("youtubeMusic", {}).get("url", None),
            }
        else:
            return {"apple_music_id": None, "youtube_music_id": None}
    except Exception as e:
        print(f" Error fetching cross-platform links: {e}")
        return {"apple_music_id": None, "youtube_music_id": None}

# Function to Fetch Spotify Playlist
def get_playlist_data(playlist_id):
    # Fetches playlist from Spotify and finds equivalent tracks on Apple Music & YouTube Music.
    try:
        playlist = sp.playlist(playlist_id)
        playlist_name = playlist["name"]
        tracks = playlist["tracks"]["items"]

        playlist_data = {
            "name": playlist_name,
            "tracks": []
        }

        for item in tracks:
            track = item["track"]
            track_id = track["id"]
            spotify_url = f"https://open.spotify.com/track/{track_id}"
            matched_links = get_matching_song(spotify_url)

            playlist_data["tracks"].append({
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "spotify_id": spotify_url,
                "apple_music_id": matched_links["apple_music_id"],
                "youtube_music_id": matched_links["youtube_music_id"]
            })

        return playlist_data

    except Exception as e:
        print(f" Error fetching playlist data: {e}")
        return None

# User Input
playlist_url = input("Enter Spotify Playlist URL or ID: ").strip()
playlist_id = playlist_url.split("/")[-1].split("?")[0]  # Extract ID from URL

# Fetch Playlist and Save to JSON
playlist_info = get_playlist_data(playlist_id)

if playlist_info:
    print("Playlist fetched successfully!")

    # Define Save Path
    save_path = r"<YOUR FOLDER PATH HERE>\playlist.json"

    # Save JSON File
    with open(save_path, "w", encoding="utf-8") as file:
        json.dump(playlist_info, file, indent=4)
    
    print(f"Playlist data saved successfully at: {save_path}")
else:
    print(" Failed to fetch playlist data.")
