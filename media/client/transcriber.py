"""
Using transcriptions and translations APIs
https://platform.openai.com/docs/guides/speech-to-text/supported-languages
"""
import os
import logging
from pydub import AudioSegment
from media.config import openai_client, CORRECT_SYS_PROMPT, OPENAI_PRICING_WHISPER, MAX_AUDIO_SIZE_IN_MB

logger = logging.getLogger()


def generate_corrected_transcript(transcript_content, model='gpt-35-turbo', temperature=0):
    response = openai_client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": CORRECT_SYS_PROMPT
            },
            {
                "role": "user",
                "content": transcript_content
            }
        ]
    )
    return response.choices[0].message.content


def chunk_audio(audio_path):
    file_name = os.path.basename(audio_path)
    file_size = os.path.getsize(audio_path)
    audio_list = []

    # Get length of audio file
    audio = AudioSegment.from_mp3(audio_path)
    duration = audio.duration_seconds
    est_cost = duration * OPENAI_PRICING_WHISPER / 60
    logger.info(f'↪ 💵 Estimated cost: ${est_cost:.2f} ({(duration / 60):.2f} minutes)')

    if file_size > MAX_AUDIO_SIZE_IN_MB * 1024 * 1024:
        logger.info(f'↪ The audio file is too large: {(file_size / 1024 / 1024):.2f} MB (>{MAX_AUDIO_SIZE_IN_MB}MB), chunking...')

        # check if chunks already exist
        if os.path.exists(f"downloads/whisper/{file_name.split('.')[0]}_0.mp3"):
            logger.info('↪ Chunks already exist, loading...')
            for i in range(100):
                chunk_name = f"downloads/whisper/{file_name.split('.')[0]}_{i}.mp3"
                if os.path.exists(chunk_name):
                    audio_list.append(chunk_name)
                else:
                    return audio_list

        audio = AudioSegment.from_mp3(audio_path)

        # PyDub handles time in milliseconds
        chunk = MAX_AUDIO_SIZE_IN_MB * 60 * 1000

        # split the audio file into ~25 minute chunks
        for i, chunk in enumerate(audio[::chunk]):
            chunk_name = f"downloads/chunks/{file_name.split('.')[0]}_{i}.mp3"

            if os.path.exists(chunk_name):
                pass

            audio_list.append(chunk_name)
            chunk.export(chunk_name, format="mp3")

    else:
        audio_list.append(audio_path)

    return audio_list


def transcript_audio(audio_path: str) -> str:
    """Translate / transcribe audio to text.

    Args:
        audio_path (str): The audio path to translate / transcribe.
        prompt (str): The prompt to use for translation.
        mode (str, optional): The mode of the request. Defaults to "translations". Can be "transcriptions".
        language (str, optional): The language of the transcription. Defaults to None. Only useful when mode is "transcriptions".
        response_format (str, optional): The format of the response. Defaults to "srt".
        timeout (float): The timeout for the request.
        max_retries (int): The maximum number of retries.

    Returns:
        str: The translated text.
    """
    logger.info(f'🗣️  Initializing Whisper transcriber...')
    audio_list = chunk_audio(audio_path)
    logger.info(f'↪ Chunk size: {len(audio_list)}')

    transcriptions = []
    for audio_file in audio_list:
        logger.info(f'\t↪ Transcribing {audio_file}...')
        file = open(audio_file, "rb")

        response = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=file,
            # response_format="text"
        )
        if "error" in response:
            error_msg = response["error"]["message"]
            raise Exception(f"⚠️ Transcription error: {error_msg}")

        # Extract the transcript from the API response
        transcript = response.text.strip()
        transcriptions.append(transcript)

    full_transcript = ' '.join(transcriptions)
    logger.info(f'↪ Total words: {len(full_transcript.split())} -- characters: {len(full_transcript)}')

    return full_transcript
