from openai import OpenAI
import speech_recognition as sr

# Configure OpenAI API
API_KEY = "Your OpenAI API key here"
client = OpenAI(api_key=API_KEY)

# Configure speech recognition
rec = sr.Recognizer()
language = 'pt-BR'
