from openai import OpenAI
from config import API_KEY
import json
import os
import time
from textblob import TextBlob
import PyPDF2

client = OpenAI(api_key=API_KEY)

HISTORY_FILE = "chat_history.json"
LOG_FILE = "chat_log.txt"
SETTINGS_FILE = "settings.json"

MAX_HISTORY = 20
FILE_CONTEXT = ""

ROLES = {
    "default": "Ты полезный ассистент.",
    "programmer": "Ты опытный программист.",
    "teacher": "Ты объясняешь просто."
}

class Colors:
    USER = '\033[94m'
    AI = '\033[92m'
    CMD = '\033[93m'
    RESET = '\033[0m'

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [{"role": "system", "content": ROLES["default"]}]

def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def log_message(user_input, reply):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"Ты: {user_input}\nAI: {reply}\n\n")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"role": "default", "short_mode": False}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

def read_file(filepath):
    if not os.path.exists(filepath):
        return None

    if filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    if filepath.endswith(".pdf"):
        text = ""
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    return None

def chat():
    global FILE_CONTEXT

    settings = load_settings()
    SHORT_MODE = settings["short_mode"]

    messages = load_history()

    stats = {"messages": 0, "tokens": 0}

    print("AI Chatbot PRO 😎")
    print("Команды: /help\n")

    while True:
        user_input = input("Ты: ")

        if user_input == "/exit":
            save_history(messages)
            break

        if user_input == "/help":
            print("""
/file путь - загрузить файл
/ask вопрос - вопрос по файлу
/search слово - поиск
/clear - очистка
/stats - статистика
/short /long - режим ответов
""")
            continue

        if user_input == "/clear":
            messages = [{"role": "system", "content": ROLES["default"]}]
            continue

        if user_input == "/stats":
            print("Сообщений:", stats["messages"])
            continue

        if user_input == "/short":
            SHORT_MODE = True
            settings["short_mode"] = True
            save_settings(settings)
            continue

        if user_input == "/long":
            SHORT_MODE = False
            settings["short_mode"] = False
            save_settings(settings)
            continue

        if user_input.startswith("/file"):
            path = user_input.split(" ", 1)[1]
            content = read_file(path)

            if content:
                FILE_CONTEXT = content[:5000]
                print("Файл загружен")
            else:
                print("Ошибка файла")
            continue

        if user_input.startswith("/ask"):
            question = user_input.split(" ", 1)[1]
            messages.append({
                "role": "user",
                "content": f"{FILE_CONTEXT}\n\n{question}"
            })
        else:
            blob = TextBlob(user_input)
            print("Эмоция:", blob.sentiment.polarity)

            messages.append({"role": "user", "content": user_input})

        messages = messages[-MAX_HISTORY:]

        start = time.time()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        end = time.time()

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        print("AI:", reply)

        stats["messages"] += 1

        save_history(messages)
        log_message(user_input, reply)

if __name__ == "__main__":
    chat()