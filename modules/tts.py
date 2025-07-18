import os
from tts import TTS
import requests

def generate_voiceover_coqui(text, output_path):
    """
    Generate TTS audio using Coqui TTS locally.
    """

    # Initialize a pre-trained model
    tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)
    tts.tts_to_file(text=text, file_path=output_path)

def generate_voiceover_elevenlabs(api_key, voice_id, text, output_path):
    """
    Generate TTS audio using ElevenLabs API.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)
