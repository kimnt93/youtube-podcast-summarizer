import re

from media.client import MediaClient
from media.client.spotify import SpotifyClient
from media.client.youtube import YouTubeClient


def create_media_client(url) -> MediaClient:
    if re.match(r'^https?://(www\.)?youtube\.com', url) or re.match(r'^https?://youtu\.be', url):
        return YouTubeClient()
    elif re.match(r'^https?://(www\.)?spotify\.com', url):
        return SpotifyClient()
    else:
        raise ValueError("Unsupported URL")
