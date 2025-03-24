import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import json
from googleapiclient.discovery import build

# Spotify API Credentials
SPOTIFY_CLIENT_ID = "YOUR_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "playlist-read-private"

# YouTube API Credentials
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"

def search_youtube(song_name, artist):
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        query = f"{song_name} {artist} audio"
        search_response = youtube.search().list(q=query, part="snippet", maxResults=1, type="video").execute()
        
        if "items" in search_response and search_response["items"]:
            video_id = search_response["items"][0]["id"].get("videoId")
            if video_id:
                return f"https://music.youtube.com/watch?v={video_id}"
        return None
    except Exception as e:
        print(f"YouTube search error: {e}")
        return None

# Initialize Spotify Client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE))

def get_matching_song(youtube_url):
    try:
        api_url = "https://api.song.link/v1-alpha.1/links"
        params = {"url": youtube_url, "userCountry": "US"}
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "spotify_id": data.get("linksByPlatform", {}).get("spotify", {}).get("url", None)
            }
        else:
            print(f"Odesli API error: {response.status_code}")
            return {"spotify_id": None}
    except Exception as e:
        print(f"Error fetching cross-platform links: {e}")
        return {"spotify_id": None}

def get_spotify_playlist(playlist_id):
    """Fetches playlist from Spotify and finds equivalent tracks on YouTube Music."""
    try:
        playlist = sp.playlist(playlist_id)
        playlist_name = playlist.get("name", "Unnamed Playlist")
        tracks = playlist.get("tracks", {}).get("items", [])
        
        playlist_data = {"name": playlist_name, "tracks": []}

        for item in tracks:
            track = item.get("track")
            if not track:
                continue
            
            track_id = track.get("id")
            spotify_url = f"https://open.spotify.com/track/{track_id}" if track_id else None
            matched_links = get_matching_song(spotify_url) if spotify_url else {"youtube_music_id": None}
            
            youtube_music_id = matched_links.get("youtube_music_id")
            if not youtube_music_id:
                youtube_music_id = search_youtube(track.get("name", ""), track.get("artists", [{}])[0].get("name", ""))
                
            playlist_data["tracks"].append({
                "name": track.get("name", "Unknown"),
                "artist": track.get("artists", [{}])[0].get("name", "Unknown"),
                "album": track.get("album", {}).get("name", "Unknown"),
                "spotify_id": spotify_url,
                "youtube_music_id": youtube_music_id
            })
        
        return playlist_data
    except Exception as e:
        print(f"Error fetching playlist data: {e}")
        return None

def get_youtube_playlist(playlist_id):
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        response = youtube.playlistItems().list(
            part="snippet", playlistId=playlist_id, maxResults=50
        ).execute()

        playlist_data = {"name": "YouTube Playlist", "tracks": []}
        for item in response.get("items", []):
            snippet = item["snippet"]
            title = snippet["title"]
            artist = snippet["videoOwnerChannelTitle"]
            youtube_url = f"https://music.youtube.com/watch?v={snippet['resourceId']['videoId']}"
            
            matched_links = get_matching_song(youtube_url)
            
            playlist_data["tracks"].append({
                "name": title,
                "artist": artist,
                "album": "Unknown",
                "spotify_id": matched_links.get("spotify_id"),
                "youtube_music_id": youtube_url
            })
        
        return playlist_data
    except Exception as e:
        print(f"Error fetching YouTube playlist data: {e}")
        return None

# User Input
playlist_url = input("Enter Playlist URL or ID: ").strip()
if "spotify" in playlist_url:
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    playlist_info = get_spotify_playlist(playlist_id)
elif "youtube" in playlist_url:
    playlist_id = playlist_url.split("list=")[-1].split("&")[0]
    playlist_info = get_youtube_playlist(playlist_id)
else:
    print("Invalid playlist URL. Must be from Spotify or YouTube Music.")
    exit()

# Fetch Playlist and Save to JSON
if playlist_info:
    print("Playlist fetched successfully!")
    save_path = input("Enter save path (e.g., playlist.json): ").strip()
    try:
        with open(save_path, "w", encoding="utf-8") as file:
            json.dump(playlist_info, file, indent=4)
        print(f"Playlist data saved at: {save_path}")
    except Exception as e:
        print(f"Error saving playlist file: {e}")
else:
    print("Failed to fetch playlist data.")
