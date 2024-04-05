import logging
import os
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import urllib.parse
import requests

logger = logging.getLogger()

_SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
_SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

if not (_SPOTIFY_CLIENT_ID and _SPOTIFY_CLIENT_SECRET):
    raise ValueError("Spotify client ID and client secret must be provided in environment variables.")

_CREDENTIAL = SpotifyClientCredentials(client_id=_SPOTIFY_CLIENT_ID, client_secret=_SPOTIFY_CLIENT_SECRET)
_CLIENT = spotipy.Spotify(auth_manager=_CREDENTIAL)


class SpotifyClient(MediaClient):
    def __init__(self):
        super().__init__()
        self.output_dir = "downloads/spotify/"
        self.download_extension = 'mp3'

    def download_mp3(self, url):
        # Parse the podcast ID from the URL
        parsed_url = urllib.parse.urlparse(url)
        podcast_id = parsed_url.path.split("/")[-1]
        logger.info(f'Podcast ID: {podcast_id}')

        # Get the first episode of the podcast
        # episode = self.sp.episode(podcast["episodes"]["items"][0]["id"])
        episode = _CLIENT.episode(podcast_id, market="US")

        # Download the audio file
        audio_url = episode["audio_preview_url"]
        response = requests.get(audio_url)
        filename = os.path.join(self.output_dir, f"{podcast_id}.{self.download_extension}")
        with open(filename, "wb") as f:
            f.write(response.content)

        logger.info(f"Episode downloaded: {filename}")

        return filename
