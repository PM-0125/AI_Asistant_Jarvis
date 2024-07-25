# modules/stt_tts.py

from google.cloud import speech
from google.cloud import texttospeech

class SpeechManager:
    def __init__(self):
        self.speech_client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()

    def speech_to_text(self, audio_file):
        with open(audio_file, 'rb') as audio:
            content = audio.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code='en-US'  # Modify for different languages
        )

        response = self.speech_client.recognize(config=config, audio=audio)
        for result in response.results:
            return result.alternatives[0].transcript

    def text_to_speech(self, text, lang='en'):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code='en-US' if lang == 'en' else 'hi-IN',
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = self.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with open('output.mp3', 'wb') as out:
            out.write(response.audio_content)
        return 'output.mp3'
