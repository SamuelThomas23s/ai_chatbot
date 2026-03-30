from openai import OpenAI
from config import API_KEY
import json
import os
import time
from textblob import TextBlob

# 🔧 Настройка ИИ
client = OpenAI(api_key=API_KEY)
HISTORY_FILE = "chat_history.json"
LOG_FILE = "chat_log.txt"
MAX_HISTORY = 20  # последние N сообщений для памяти

# 🎭 роли ассистента
ROLES = {
    "default": "Ты полезный ассистент.",
    "programmer": "Ты опытный программист, объясняешь код просто.",
    "marketer": "Ты эксперт по маркетингу и продажам.",
    "teacher": "Ты учитель, объясняешь понятно и с примерами."
}

# 🎨 цвета вывода
class Colors:
    USER = '\033[94m'
    AI = '\033[92m'
    CMD = '\033[93m'
    RESET = '\033[0m'

# 💾 загрузка истории
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [{"role": "system", "content": ROLES["default"]}]

# 💾 сохранение истории
def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

# 📝 логирование диалога
def log_message(user_input, reply):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"Ты: {user_input}\nAI: {reply}\n\n")

# 🌟 главный цикл чата
def chat():
    print(f"{Colors.CMD}AI Chatbot PRO 😎")
    print("Команды: /exit /clear /role /save /help /search /short /long\n" + Colors.RESET)

    messages = load_history()
    SHORT_MODE = False

    while True:
        user_input = input(f"{Colors.USER}Ты: {Colors.RESET}")

        # 🚪 выход
        if user_input.lower() == "/exit":
            save_history(messages)
            print(f"{Colors.CMD}История сохранена. Пока!{Colors.RESET}")
            break

        # 🧹 очистка истории
        if user_input.lower() == "/clear":
            messages = [{"role": "system", "content": ROLES["default"]}]
            save_history(messages)
            print(f"{Colors.CMD}История очищена!{Colors.RESET}")
            continue

        # 🎭 смена роли
        if user_input.lower().startswith("/role"):
            print(f"{Colors.CMD}Доступные роли: {', '.join(ROLES.keys())}{Colors.RESET}")
            role = input(f"{Colors.CMD}Выбери роль: {Colors.RESET}")
            if role in ROLES:
                messages = [{"role": "system", "content": ROLES[role]}]
                save_history(messages)
                print(f"{Colors.CMD}Роль изменена на: {role}{Colors.RESET}")
            else:
                print(f"{Colors.CMD}Такой роли нет{Colors.RESET}")
            continue

        # 💾 ручное сохранение
        if user_input.lower() == "/save":
            save_history(messages)
            print(f"{Colors.CMD}История сохранена!{Colors.RESET}")
            continue

        # ℹ️ помощь
        if user_input.lower() == "/help":
            print(f"""{Colors.CMD}
Доступные команды:
/exit  - выйти из чата
/clear - очистить историю
/role  - сменить роль ассистента
/save  - сохранить историю
/help  - показать эту справку
/search <слово> - поиск по истории
/short - краткие ответы
/long - длинные ответы
{Colors.RESET}""")
            continue

        # 🔎 поиск по истории
        if user_input.lower().startswith("/search"):
            term = user_input.split(" ", 1)[1] if " " in user_input else ""
            found = [m["content"] for m in messages if term.lower() in m["content"].lower()]
            if found:
                print(f"{Colors.CMD}Найдено в истории:{Colors.RESET}")
                for f in found:
                    print("-", f)
            else:
                print(f"{Colors.CMD}Совпадений не найдено{Colors.RESET}")
            continue

        # ✂️ режим коротких/длинных ответов
        if user_input.lower() == "/short":
            SHORT_MODE = True
            print(f"{Colors.CMD}Режим коротких ответов включён ✅{Colors.RESET}")
            continue
        if user_input.lower() == "/long":
            SHORT_MODE = False
            print(f"{Colors.CMD}Режим длинных ответов включён ✅{Colors.RESET}")
            continue

        # 🧠 анализ эмоций
        blob = TextBlob(user_input)
        polarity = blob.sentiment.polarity
        if polarity > 0.1:
            mood = "Позитивное сообщение 😊"
        elif polarity < -0.1:
            mood = "Негативное сообщение 😢"
        else:
            mood = "Нейтральное сообщение 😐"
        print(f"{Colors.CMD}[Эмоция]: {mood}{Colors.RESET}")

        # обычный чат
        system_message = "Ты полезный ассистент."
        if SHORT_MODE:
            system_message += " Давай очень короткие ответы."
        messages[0]["content"] = system_message

        messages.append({"role": "user", "content": user_input})
        messages = messages[-MAX_HISTORY:]  # последние N сообщений

        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        end_time = time.time()

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        print(f"{Colors.AI}AI ({end_time - start_time:.2f} сек): {reply}{Colors.RESET}")

        save_history(messages)
        log_message(user_input, reply)

if __name__ == "__main__":
    chat()