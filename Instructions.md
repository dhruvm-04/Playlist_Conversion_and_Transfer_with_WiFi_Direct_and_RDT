# **How to Run**
## **Requirements**
Before proceeding, make sure you have the following libraries and packages installed on your system.
Alternatively, you may use the `lib_reqs.txt` text file to install all packages simultaneously.
Use command `pip install -r lib_reqs.txt` on your command prompt.
- ```sh
  pip install spotipy
  pip install requests
  pip install cryptography
  pip install pywifi
  pip install ytmusicapi
  pip install google-auth-oauthlib
  pip install google-api-python-client
- In case of any issues, check the installations using `pip list | grep -E "spotipy|requests|cryptography|pywifi|ytmusicapi"`

## **Steps to Run**

  - Before running `get_playlist.py`, create an app on sporify developer dashboard and update the id variables with your credentials. After that, please change the file path in the `receiver_rdt_wifi_direct.py` file to the one on your system.
  - Similarly, for the YT Music API, get your cookie id and authentication id from the inspect element network tab and create a json file named headers_auth with those 2 to use in the code.
      
   - ### **Fetch a Spotify Playlist**
      ```sh
      python get_playlist.py
   
   - ### **Send/Receive Playlist Over Wi-Fi Direct (Sender)**
     ```sh
     python sender_receiver.py
   
   - ### **Create Playlist on Platform**
     ```sh
     python create.py
