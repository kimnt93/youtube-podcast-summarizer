from media.client.transcriber import transcript_audio, generate_corrected_transcript


class MediaClient:
    def __init__(self):
        self.output_dir = None
        self.download_extension = None

    def get_transcript(self, url, correct_transcript=False, **correct_transcript_kwargs):
        saved_file_path = self.download_mp3(url)
        transcript_content = transcript_audio(saved_file_path)

        if correct_transcript:
            transcript_content = generate_corrected_transcript(transcript_content, **correct_transcript_kwargs)

        return transcript_content

    def download_mp3(self, url):
        raise NotImplementedError
