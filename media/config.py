import os
import logging
import openai
from openai import OpenAI
from dataclasses import dataclass
from openai import AzureOpenAI

logger = logging.getLogger()

CORRECT_SYS_PROMPT = "You are a helpful assistant for the company ZyntriQix. Your task is to correct any spelling discrepancies in the transcribed text. Make sure that the names of the following products are spelled correctly: ZyntriQix, Digique Plus, CynapseFive, VortiQore V8, EchoNix Array, OrbitalLink Seven, DigiFractal Matrix, PULSE, RAPT, B.R.I.C.K., Q.U.A.R.T.Z., F.L.I.N.T. Only add necessary punctuation such as periods, commas, and capitalization, and use only the context provided."
CORRECT_TEMPERATURE = 0
MAX_AUDIO_SIZE_IN_MB = 22
OPENAI_PRICING_WHISPER = 0.006
LANGUAGE_PRIORITIES = ["en", "vi"]


@dataclass
class CeleryConfiguration:
    BROKER = os.environ['CELERY_BROKER']
    BACKEND = os.environ['CELERY_BACKEND']


# setup openai
_BASE_URL = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
if "api.openai.com" in _BASE_URL:
    openai.base_url = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
    openai.api_key = os.environ['OPENAI_API_KEY']
    openai_client = OpenAI()
else:
    # create azure client
    openai_client = AzureOpenAI(
        # https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning
        # api_version="2023-07-01-preview",
        # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
        azure_endpoint=_BASE_URL,
        api_key=os.environ['OPENAI_API_KEY'],
        api_version=os.environ['API_VERSION']
    )
