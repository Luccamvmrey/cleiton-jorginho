from pathlib import Path
from config import *
import pygame
import keyboard
import warnings

# Ignore deprecation on stream_to_file method
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configure audio file path
AUDIO_FILE_PATH = Path(__file__).parent / "audios" / "output.mp3"
OUTPUT_DIR = AUDIO_FILE_PATH.parent

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

if not AUDIO_FILE_PATH.exists():
    AUDIO_FILE_PATH.touch()


# Play audio file
def play_audio(file_path):
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if keyboard.is_pressed("space"):
                pygame.mixer.music.stop()
                print("\n##### Reprodução interrompida. #####")
                return
    except pygame.error as e:
        print(f"Erro ao reproduzir áudio: {str(e)}")
    finally:
        pygame.quit()


# Convert speech to text
def speech_to_text(audio):
    try:
        text = rec.recognize_google(audio, language=language)
        return text
    except Exception as e:
        print("Falha no reconhecimento de voz " + str(e))
        return ""


# Convert text to speech
def text_to_speech(text, speed=1.0):
    response = client.audio.speech.create(
        model="tts-1",
        voice="echo",
        input=text,
        speed=speed
    )
    print(text)
    response.stream_to_file(AUDIO_FILE_PATH)
    play_audio(AUDIO_FILE_PATH)
