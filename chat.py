import requests
import json
import re
import sys

from util import *
from config import *
from queries import *
from message import Message
from audio import speech_to_text, text_to_speech

CHAT_HISTORY = []


def start_chat():
    messages = [
        {"role": "system", "content": system_query_intro},
        {"role": "system", "content": system_query_classes},
        {"role": "system", "content": system_query_general}
    ]
    CHAT_HISTORY.extend(messages)
    print("Cleiton online.")

    with sr.Microphone() as mic:
        rec.adjust_for_ambient_noise(mic)
        while True:
            try:
                text = listen_and_return_text()

                if "e aí cleiton" in text.lower():
                    try:
                        make_a_question(text)
                    except Exception as e:
                        print(f"exception: {e}")
                elif "cleiton sair" in text.lower():
                    text_to_speech("Saindo...")
                    sys.exit()
            except sr.WaitTimeoutError:
                pass


# Returns the listened audio as text
def listen_and_return_text():
    with sr.Microphone() as mic:
        rec.adjust_for_ambient_noise(mic)

        print("Ouvindo...")
        listened_audio = rec.listen(mic, timeout=5, phrase_time_limit=10)
        print("Processando...")

        text = speech_to_text(listened_audio)

    return text


# Check if user wants to end chat
def check_end_chat(text):
    if "cleiton sair" in text.lower():
        text_to_speech("Saindo...")
        sys.exit()
    elif "tchau cleiton" in text.lower():
        text_to_speech("Tchau, estarei por aqui se precisar...")


# Consult chatGPT
def generate_prompt(user_input):
    message = Message(role="user", content=user_input)
    CHAT_HISTORY.append(message.full_message())

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=CHAT_HISTORY
    )
    print("Pensando...")
    chat_answer = response.choices[0].message.content

    message = Message(role="assistant", content=chat_answer)
    CHAT_HISTORY.append(message.full_message())

    return chat_answer


def extract_info(response):
    info_pattern = re.compile(r'\*(.*?)\*')
    info = re.search(info_pattern, response)

    if info:
        info = info.group(1)
    else:
        info = None

    modified_response = re.sub(info_pattern, '', response)
    return modified_response.strip(), info


def extract_url_from_response(response):
    # Extract parameters from OpenAI response content using regex
    url_pattern = re.compile(r'`([^`]+)`')
    url = re.search(url_pattern, response)

    if url:
        url = url.group(1)
    else:
        url = None

    modified_response = re.sub(url_pattern, '', response)
    return modified_response.strip(), url


def has_parameters(url):
    if '?' in url:
        params = url.split('?')[1]
        return len(params) > 0 and params.lower() != "none"
    return False


def query_classes_api(url_params):
    url = f"https://mimir-api.vercel.app{url_params}"
    print(url)
    api_response = None

    try:
        response = requests.get(url)
        response.raise_for_status()
        api_response = response.json()
    except requests.exceptions.RequestException as e:
        print("Erro na requisição:", e)
    except json.JSONDecodeError as e:
        print("Erro ao decodificar JSON:", e)
        api_response = None

    return api_response


def get_class_info(classes_response):
    final_message = ""
    for class_info in classes_response:
        class_info["dayOfWeek"] = transform_day_of_week(class_info["dayOfWeek"])
        class_info["group"] = transform_group(class_info["group"])

        response = (f"A aula do professor {class_info['professorName']} será na sala"
                    f" {class_info['room']['roomNumber']} no {class_info['room']['roomFloor']}º"
                    f" andar na {class_info['dayOfWeek']} às {class_info['timeIn']}")

        final_message += response + "\n"

    CHAT_HISTORY.append({"role": "assistant", "content": final_message})
    return final_message


def handle_user_input(user_input):
    response = generate_prompt(user_input)

    modified_response, extracted_info = extract_info(response)
    print(modified_response, extracted_info)

    final_response = None

    if extracted_info == "Aulas/Eventos":
        modified_response, url = extract_url_from_response(modified_response)
        print(modified_response, url)

        if not has_parameters(url):
            final_response = modified_response
        else:
            classes_response = query_classes_api(url)
            final_response = get_class_info(classes_response)

    elif extracted_info == "Geral":
        final_response = modified_response

    return final_response


# Make a question
def make_a_question(text):
    print(text)
    if text.lower() == "e aí cleiton":
        message = Message(role="assistant", content="Oi, Como posso te ajudar hoje?")
        CHAT_HISTORY.append(message.full_message())
        text_to_speech("Oi, Como posso te ajudar hoje?", 1.0)
    else:
        response = handle_user_input(text)
        text_to_speech(response, 1.0)

    with sr.Microphone() as mic:
        rec.adjust_for_ambient_noise(mic)
        while True:
            try:
                text = listen_and_return_text()
                check_end_chat(text)

                if not text:
                    response = handle_user_input(text)
                    text_to_speech(response, 1.0)

                    text = listen_and_return_text()
                    check_end_chat(text)

                response = handle_user_input(text)
                text_to_speech(response, 1.0)
            except sr.WaitTimeoutError:
                pass
