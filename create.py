import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

CLIENT_SECRETS_FILE = r"C:\Dhruv\PESU\Subjects\Sem 4\CN\MiniProject\trials\oauth.json"


def authenticate_youtube():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES
    )
    credentials = flow.run_local_server(port=0)
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)


def create_playlist(youtube, playlist_name):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": playlist_name, "description": "Created via API", "tags": ["music"], "defaultLanguage": "en"},
            "status": {"privacyStatus": "public"},
        },
    )
    response = request.execute()
    return response["id"]


def add_video_to_playlist(youtube, playlist_id, video_id):
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


def main():
    with open(r"C:\Dhruv\PESU\Subjects\Sem 4\CN\MiniProject\trials\newplst.json", "r", encoding="utf-8") as file:
        playlist_data = json.load(file)
    
    youtube = authenticate_youtube()
    playlist_id = create_playlist(youtube, playlist_data["name"])
    
    for track in playlist_data["tracks"]:
        if "youtube_music_id" in track and track["youtube_music_id"]:
            video_id = track["youtube_music_id"].split("?")[-1].split("=")[-1]
            add_video_to_playlist(youtube, playlist_id, video_id)

    print(f"Playlist '{playlist_data['name']}' created successfully.")


if __name__ == "__main__":
    main()
