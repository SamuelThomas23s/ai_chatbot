from openai import OpenAI
from config import API_KEY
import json
import os
import time
from textblob import TextBlob
import PyPDF2

# 🔧 ИИ клиент
client = OpenAI(api_key=API_KEY)

# 📁 файлы
HISTORY_FILE = "chat_history.json"
LOG_FILE = "chat_log.txt"
SETTINGS_FILE = "settings.json"

# ⚙️ настройки
MAX_HISTORY = 20
FILE_CONTEXT = ""
EXPERT_MODE = False

# 🎭 роли
ROLES = {
    "default": "Ты полезный ассистент.",
    "programmer": "Ты опытный программист.",
    "teacher": "Ты объясняешь просто и понятно.",
    "marketer": "Ты эксперт по маркетингу."
}

# 🎨 цвета
class Colors:
    USER = '\033[94m'
    AI = '\033[92m'
    CMD = '\033[93m'
    RESET = '\033[0m'


# 💾 история
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [{"role": "system", "content": ROLES["default"]}]


def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


# 📝 лог
def log_message(user_input, reply):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"Ты: {user_input}\nAI: {reply}\n\n")


# ⚙️ настройки
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"role": "default", "short_mode": False}


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


# 📂 чтение файлов
def read_file(path):
    if not os.path.exists(path):
        return None

    if path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    if path.endswith(".pdf"):
        text = ""
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    return None


# 🧠 сжатие памяти
def summarize_history(messages):
    if len(messages) < 10:
        return messages

    old = messages[:-10]
    recent = messages[-10:]

    text = "\n".join([m["content"] for m in old if m["role"] != "system"])

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Сожми текст в краткое резюме."},
                {"role": "user", "content": text}
            ]
        )

        summary = response.choices[0].message.content

        return [
            {"role": "system", "content": f"Память: {summary}"}
        ] + recent

    except:
        return messages


# 🚀 чат
def chat():
    global FILE_CONTEXT, EXPERT_MODE

    settings = load_settings()
    SHORT_MODE = settings["short_mode"]

    messages = load_history()
    stats = {"messages": 0, "tokens": 0}

    print(f"{Colors.CMD}AI Chatbot PRO 🚀")
    print("Команды: /help /expert /normal\n")

    while True:
        user_input = input(f"{Colors.USER}Ты: {Colors.RESET}")

        # 🚪 выход
        if user_input == "/exit":
            save_history(messages)
            print("Пока!")
            break

        # ℹ️ help
        if user_input == "/help":
            print("""
/file путь      - загрузить файл
/ask вопрос     - вопрос по файлу
/search слово   - поиск в истории
/short /long    - режим ответов
/expert         - режим эксперта
/normal         - обычный режим
/stats          - статистика
/reset_all      - полный сброс
/exit           - выход
""")
            continue

        # 🧠 режим эксперта
        if user_input == "/expert":
            EXPERT_MODE = True
            print("Режим эксперта включён 🧠")
            continue

        if user_input == "/normal":
            EXPERT_MODE = False
            print("Обычный режим включён")
            continue

        # 🔄 сброс
        if user_input == "/reset_all":
            messages = [{"role": "system", "content": ROLES["default"]}]
            FILE_CONTEXT = ""
            stats = {"messages": 0, "tokens": 0}
            print("Всё очищено!")
            continue

        # 📊 stats
        if user_input == "/stats":
            print(stats)
            continue

        # ✂️ режим ответов
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

        # 📂 файл
        if user_input.startswith("/file"):
            path = user_input.split(" ", 1)[1]
            content = read_file(path)

            if content:
                FILE_CONTEXT = content[:5000]
                print("Файл загружен")
            else:
                print("Ошибка файла")
            continue

        # ❓ вопрос по файлу
        if user_input.startswith("/ask"):
            question = user_input.split(" ", 1)[1]

            messages.append({
                "role": "user",
                "content": f"Контекст файла:\n{FILE_CONTEXT}\n\nВопрос: {question}"
            })

        else:
            # 😄 эмоции
            polarity = TextBlob(user_input).sentiment.polarity
            mood = "😊" if polarity > 0 else "😢" if polarity < 0 else "😐"
            print(f"{Colors.CMD}Эмоция: {mood}{Colors.RESET}")

            messages.append({"role": "user", "content": user_input})

        # 🧠 ограничение памяти
        if len(messages) > 40:
            messages = summarize_history(messages)

        # 🎯 system message
        system_message = "Ты полезный ассистент."

        if SHORT_MODE:
            system_message += " Отвечай максимально кратко."

        if EXPERT_MODE:
            system_message = """
Ты эксперт. Отвечай профессионально:

1. Если вопрос неясный — задай уточняющий вопрос
2. Давай структурированный ответ:

📌 Проблема
💡 Решение
⚠️ Риски
✅ Итог
"""

        messages[0]["content"] = system_message

        start = time.time()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        end = time.time()

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        print(f"{Colors.AI}AI ({end-start:.2f}s): {reply}{Colors.RESET}")

        stats["messages"] += 1
        stats["tokens"] += len(user_input) + len(reply)

        save_history(messages)
        log_message(user_input, reply)


if __name__ == "__main__":
    chat()