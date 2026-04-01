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
MAX_HISTORY = 20

ROLES = {
    "default": "Ты полезный ассистент.",
    "programmer": "Ты опытный программист.",
    "teacher": "Ты объясняешь максимально просто."
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

# 📂 Чтение файла
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
    print(f"{Colors.CMD}AI Chatbot PRO+ 😎")
    print("Команды: /file /exit /clear /role /help\n" + Colors.RESET)

    messages = load_history()
    SHORT_MODE = False

    while True:
        user_input = input(f"{Colors.USER}Ты: {Colors.RESET}")

        # выход
        if user_input == "/exit":
            save_history(messages)
            break

        # 📂 анализ файла
        if user_input.startswith("/file"):
            path = user_input.split(" ", 1)[1] if " " in user_input else ""

            content = read_file(path)

            if not content:
                print(f"{Colors.CMD}Не удалось прочитать файл{Colors.RESET}")
                continue

            print(f"{Colors.CMD}Файл загружен, анализируем...{Colors.RESET}")

            messages.append({
                "role": "user",
                "content": f"Проанализируй этот текст:\n{content[:3000]}"
            })

        else:
            # эмоции
            blob = TextBlob(user_input)
            polarity = blob.sentiment.polarity
            mood = "😊" if polarity > 0 else "😢" if polarity < 0 else "😐"
            print(f"{Colors.CMD}Эмоция: {mood}{Colors.RESET}")

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

        print(f"{Colors.AI}AI ({end-start:.2f}s): {reply}{Colors.RESET}")

        save_history(messages)
        log_message(user_input, reply)

if __name__ == "__main__":
    chat()