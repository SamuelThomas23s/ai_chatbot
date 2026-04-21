from openai import OpenAI
from config import API_KEY
import json
import os
import time
from textblob import TextBlob
import PyPDF2
import requests

client = OpenAI(api_key=API_KEY)

# 📁 файлы
HISTORY_FILE = "chat_history.json"
LOG_FILE = "chat_log.txt"
SETTINGS_FILE = "settings.json"

# ⚙️ настройки
MAX_HISTORY = 20
FILE_CONTEXT = ""

# 🧠 новые режимы
PERSONA = ""
PINNED_KNOWLEDGE = ""
AUTO_MODE = False
EXPERT_MODE = False

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
    return [{"role": "system", "content": "Ты полезный ассистент."}]


def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


# 📝 лог
def log_message(user_input, reply):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"Ты: {user_input}\nAI: {reply}\n\n")


# 📂 файл
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


# 🌐 web (простая версия)
def web_search(query):
    try:
        url = f"https://duckduckgo.com/?q={query}&format=json"
        r = requests.get(url)
        return r.text[:1500]
    except:
        return "Ошибка поиска"


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

        return [{"role": "system", "content": f"Память: {summary}"}] + recent

    except:
        return messages


# 🚀 чат
def chat():
    global FILE_CONTEXT, PERSONA, PINNED_KNOWLEDGE, AUTO_MODE, EXPERT_MODE

    messages = load_history()
    stats = {"messages": 0, "tokens": 0}

    print(f"{Colors.CMD}AI CHATBOT PRO MAX 🚀{Colors.RESET}")
    print("Напиши /help для команд\n")

    while True:
        user_input = input(f"{Colors.USER}Ты: {Colors.RESET}")

        # 🚪 exit
        if user_input == "/exit":
            save_history(messages)
            break

        # 📌 help
        if user_input == "/help":
            print("""
/file <path>
/ask <question>
/web <query>
/persona <text>
/pin <text>
/auto /manual
/expert /normal
/stats
/reset
/exit
""")
            continue

        # 🧠 persona
        if user_input.startswith("/persona"):
            PERSONA = user_input.split(" ", 1)[1]
            print("Persona обновлена 🧠")
            continue

        # 📌 pin
        if user_input.startswith("/pin"):
            PINNED_KNOWLEDGE = user_input.split(" ", 1)[1]
            print("Закреплено 📌")
            continue

        # ⚡ auto
        if user_input == "/auto":
            AUTO_MODE = True
            print("AUTO MODE включён ⚡")
            continue

        if user_input == "/manual":
            AUTO_MODE = False
            print("AUTO MODE выключен")
            continue

        # 🎭 expert
        if user_input == "/expert":
            EXPERT_MODE = True
            print("Expert mode 🧠")
            continue

        if user_input == "/normal":
            EXPERT_MODE = False
            print("Normal mode")
            continue

        # 📊 stats
        if user_input == "/stats":
            print(stats)
            continue

        # 🧹 reset
        if user_input == "/reset":
            messages = [{"role": "system", "content": "Ты полезный ассистент."}]
            FILE_CONTEXT = ""
            print("Сброс выполнен")
            continue

        # 📂 file
        if user_input.startswith("/file"):
            path = user_input.split(" ", 1)[1]
            FILE_CONTEXT = read_file(path) or ""
            print("Файл загружен 📂")
            continue

        # 🌐 web
        if user_input.startswith("/web"):
            query = user_input.split(" ", 1)[1]
            result = web_search(query)

            messages.append({
                "role": "user",
                "content": f"WEB DATA:\n{result}\n\nQuestion: {query}"
            })

        else:
            # 😄 mood
            polarity = TextBlob(user_input).sentiment.polarity
            mood = "😊" if polarity > 0 else "😢" if polarity < 0 else "😐"
            print(f"{Colors.CMD}Mood: {mood}{Colors.RESET}")

            messages.append({"role": "user", "content": user_input})

        # 🧠 memory limit
        if len(messages) > 40:
            messages = summarize_history(messages)

        # 🎯 system prompt
        system = "Ты полезный ассистент."

        if PERSONA:
            system += f"\nPersona: {PERSONA}"

        if PINNED_KNOWLEDGE:
            system += f"\nUser info: {PINNED_KNOWLEDGE}"

        if AUTO_MODE:
            system += "\nТы работаешь в AUTO MODE: уточняй, предлагай варианты."

        if EXPERT_MODE:
            system += "\nОтвет структурированный: проблема / решение / риски / итог."

        messages[0]["content"] = system

        # 🤖 AI request
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