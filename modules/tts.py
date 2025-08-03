
from gtts import gTTS
try:
    from TTS.api import TTS
except ImportError:
    TTS = None

def generate_voiceover_fallback(text, output_path):
    tts = gTTS(text, lang="en")
    tts.save(output_path)

def generate_voiceover_coqui(text, output_path):
    """
    Generate TTS audio using Coqui TTS locally.
    """
    if TTS is None:
        raise ImportError("Coqui TTS is not installed. Please install the 'TTS' package.")
    try:
        tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)
        tts.tts_to_file(text=text, file_path=output_path)
    except Exception as e:
        print(f"[Coqui TTS] Error: {e}")
        raise


