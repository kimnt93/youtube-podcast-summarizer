"""
https://www.youtube.com/watch?v=arj7oStGLkU&ab_channel=TED  # multi-languages
https://youtu.be/gcabLj76ziw?si=H7XnXOJevy5ejai_  # auto generated-vietnamese
https://youtu.be/u0PnohAr1Kg?si=OsXF31U3bwu0IK5x  # no cc
"""
import hashlib
import logging
import os
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from urllib.parse import urlparse, parse_qs

from media.client import MediaClient
from media.client.transcriber import generate_corrected_transcript, transcript_audio
from media.config import LANGUAGE_PRIORITIES

logger = logging.getLogger()


def extract_video_id(url):
    parsed_url = urlparse(url)
    if "youtu.be" in parsed_url.netloc:
        # For shortened URLs like https://youtu.be/kF1nTG8l7B0?si=xWKIPMB-EI81R9fp
        video_id = parsed_url.path.lstrip("/")
    elif "youtube.com" in parsed_url.netloc:
        # For full URLs like https://www.youtube.com/watch?v=kF1nTG8l7B0&ab_channel=PSMH
        video_id = parse_qs(parsed_url.query).get('v', [None])[0]
    else:
        # Not a valid YouTube URL
        video_id = None
    return video_id


class YouTubeClient(MediaClient):
    def __init__(self):
        super().__init__()
        self.output_dir = "downloads/youtube/"
        self.download_extension = 'mp3'

    def get_transcript(self, url, correct_transcript=False, **correct_transcript_kwargs):
        video_id = extract_video_id(url)
        default_language = None
        transcript_content = None
        try:
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

            # find transcript from default (auto-generated)
            for transcript in transcripts:
                """
                transcript.video_id,
                transcript.language,
                transcript.language_code,
                transcript.is_generated,
                transcript.is_translatable,
                transcript.translation_languages,
                """
                if transcript.is_generated:  # found default language
                    default_language = transcript.language_code
                    break  # set default language and stop iteration
                elif transcript.language_code in LANGUAGE_PRIORITIES:  # manual script
                    default_language = transcript.language_code
                else:
                    pass
        except TranscriptsDisabled:
            logger.exception("TranscriptsDisabled error...")
        except Exception as ex:
            logger.exception(ex)
            # raise NotImplementedError("Unknown exception, download video and generate transcript using openai")

        if default_language is not None:
            subtitles = YouTubeTranscriptApi.get_transcript(video_id, languages=[default_language])
            transcript_content = " ".join([x['text'] for x in subtitles])
        else:
            # call OpenAI whisper
            saved_file_path = self.download_mp3(url)
            transcript_content = transcript_audio(saved_file_path)

        if correct_transcript:
            transcript_content = generate_corrected_transcript(transcript_content, **correct_transcript_kwargs)

        return transcript_content

    def download_mp3(self, url):
        video_id = extract_video_id(url)
        output_path = os.path.join(self.output_dir, f'{hashlib.md5(video_id.encode()).hexdigest()}.{self.download_extension}')
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # using pytube
        ##
        #
        # # download the MP3
        # out_file = YouTube(video_url).streams.filter(only_audio=True).first().download(output_path=self.output_dir)
        #
        # # rename the file
        # base, ext = os.path.splitext(out_file)
        # new_MP3_file = base + '.mp3'
        # os.rename(out_file, new_MP3_file)

        # or yt_dl
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.download_extension,
            }],
            'outtmpl': output_path.replace(f".{self.download_extension}", "")
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download([video_url])
        logger.info(f"Download url ```{video_url}``` return status code ```{error_code}```")
        return output_path


if __name__ == "__main__":
    test_cases = [
        # "https://www.youtube.com/watch?v=arj7oStGLkU&ab_channel=TED",  # multi-languages
        # "https://www.youtube.com/watch?v=gcabLj76ziw&ab_channel=Spiderum",  # auto generated-vietnamese
        "https://www.youtube.com/watch?v=u0PnohAr1Kg&ab_channel=VTV24",  # no cc
    ]
    yt = YouTubeClient()
    for test_case in test_cases:
        logger.info("=================================")
        transcript = yt.get_transcript(video_url=test_case)
        logger.info(test_case)
        print(f"Transcript audio:\n{transcript}")
