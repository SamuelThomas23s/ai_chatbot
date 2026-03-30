from openai import OpenAI
from config import API_KEY
import json
import os
import time

client = OpenAI(api_key=API_KEY)

HISTORY_FILE = "chat_history.json"
LOG_FILE = "chat_log.txt"
MAX_HISTORY = 20  # Максимальное количество последних сообщений для памяти

# 🎭 роли
ROLES = {
    "default": "Ты полезный ассистент.",
    "programmer": "Ты опытный программист, объясняешь код просто.",
    "marketer": "Ты эксперт по маркетингу и продажам.",
    "teacher": "Ты учитель, объясняешь понятно и с примерами."
}

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

def chat():
    print("AI Chatbot PRO 😎")
    print("Команды: /exit /clear /role /save /help\n")

    messages = load_history()

    while True:
        user_input = input("Ты: ")

        # 🚪 выход
        if user_input.lower() == "/exit":
            save_history(messages)
            print("История сохранена. Пока!")
            break

        # 🧹 очистка памяти
        if user_input.lower() == "/clear":
            messages = [{"role": "system", "content": ROLES["default"]}]
            save_history(messages)
            print("История очищена!")
            continue

        # 🎭 смена роли
        if user_input.lower().startswith("/role"):
            print("Доступные роли:", ", ".join(ROLES.keys()))
            role = input("Выбери роль: ")

            if role in ROLES:
                messages = [{"role": "system", "content": ROLES[role]}]
                save_history(messages)
                print(f"Роль изменена на: {role}")
            else:
                print("Такой роли нет")
            continue

        # 💾 ручное сохранение
        if user_input.lower() == "/save":
            save_history(messages)
            print("История сохранена!")
            continue

        # ℹ️ помощь
        if user_input.lower() == "/help":
            print("""
Доступные команды:
/exit  - выйти из чата
/clear - очистить историю
/role  - сменить роль ассистента
/save  - сохранить историю
/help  - показать эту справку
""")
            continue

        # обычный чат
        messages.append({"role": "user", "content": user_input})
        messages = messages[-MAX_HISTORY:]  # оставляем только последние N сообщений

        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        end_time = time.time()

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        print(f"AI ({end_time - start_time:.2f} сек):", reply)

        save_history(messages)
        log_message(user_input, reply)

if __name__ == "__main__":
    chat()