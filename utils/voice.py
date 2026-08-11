import io
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class VoiceProcessor:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")
        self.client = OpenAI(api_key=api_key)

    def transcribe_audio(
        self,
        audio_file_path: str | Path,
    ) -> str:
        with open(audio_file_path, "rb") as f:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
            )
        return transcript.text

    def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
    ) -> str:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename
        
        transcript = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
        return transcript.text

    def text_to_speech(
        self,
        text: str,
        output_file_path: str | Path,
        voice: str = "alloy",
    ) -> str:
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
        )
        
        output_file_path = Path(output_file_path)
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file_path, "wb") as f:
            f.write(response.content)
        
        return str(output_file_path)

    def text_to_speech_bytes(
        self,
        text: str,
        voice: str = "alloy",
    ) -> bytes:
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
        )
        return response.content
