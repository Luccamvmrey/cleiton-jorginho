from openai import OpenAI
import speech_recognition as sr

# Configure OpenAI API
API_KEY = "sk-proj-QTqiu0QpMRCe9JEE6yGYT3BlbkFJMID4qCRtBW3mDQpAblRa"
client = OpenAI(api_key=API_KEY)

# Configure speech recognition
rec = sr.Recognizer()
language = 'pt-BR'
