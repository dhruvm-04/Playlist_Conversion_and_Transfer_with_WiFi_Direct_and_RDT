import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SCOPES_YT = ["https://www.googleapis.com/auth/youtube.force-ssl"]
SCOPES_SPOTIFY = ["playlist-modify-public", "playlist-modify-private"]

CLIENT_SECRETS_FILE = r"C:\Dhruv\PESU\Subjects\Sem 4\CN\MiniProject\trials\oauth.json"
SPOTIFY_CLIENT_ID = "YOUR_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback"

def authenticate_youtube():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES_YT
    )
    credentials = flow.run_local_server(port=0)
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def authenticate_spotify():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=" ".join(SCOPES_SPOTIFY)
    ))

def create_youtube_playlist(youtube, playlist_name):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": playlist_name, "description": "Created via API", "tags": ["music"], "defaultLanguage": "en"},
            "status": {"privacyStatus": "public"},
        },
    )
    response = request.execute()
    return response["id"]

def add_video_to_youtube_playlist(youtube, playlist_id, video_id):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            }
        },
    )
    request.execute()

def create_spotify_playlist(spotify, playlist_name):
    user_id = spotify.me()["id"]
    playlist = spotify.user_playlist_create(user=user_id, name=playlist_name, public=True)
    return playlist["id"]

def add_track_to_spotify_playlist(spotify, playlist_id, track_uri):
    spotify.playlist_add_items(playlist_id, [track_uri])

def main():
    with open("playlist.json", "r", encoding="utf-8") as file:
        playlist_data = json.load(file)
    
    choice = input("Would you like to upload to YouTube Music or Spotify? (yt/spotify): ").strip().lower()
    
    if choice == "yt":
        youtube = authenticate_youtube()
        youtube_playlist_id = create_youtube_playlist(youtube, playlist_data["name"])
        for track in playlist_data["tracks"]:
            if "youtube_music_id" in track and track["youtube_music_id"]:
                video_id = track["youtube_music_id"].split("?")[-1].split("=")[-1]
                add_video_to_youtube_playlist(youtube, youtube_playlist_id, video_id)
        print(f"Playlist '{playlist_data['name']}' created successfully on YouTube Music.")
    
    elif choice == "spotify":
        spotify = authenticate_spotify()
        spotify_playlist_id = create_spotify_playlist(spotify, playlist_data["name"])
        for track in playlist_data["tracks"]:
            if "spotify_id" in track and track["spotify_id"]:
                add_track_to_spotify_playlist(spotify, spotify_playlist_id, track["spotify_id"])
        print(f"Playlist '{playlist_data['name']}' created successfully on Spotify.")
    
    else:
        print("Invalid choice. Please enter 'yt' for YouTube Music or 'spotify' for Spotify.")

if __name__ == "__main__":
    main()
