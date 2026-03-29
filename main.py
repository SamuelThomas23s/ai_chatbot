from openai import OpenAI
from config import API_KEY
import json
import os

client = OpenAI(api_key=API_KEY)

HISTORY_FILE = "chat_history.json"

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

def chat():
    print("AI Chatbot PRO 😎")
    print("Команды: /clear /role /save /exit\n")

    messages = load_history()

    while True:
        user_input = input("Ты: ")

        # 🚪 выход
        if user_input.lower() == "/exit":
            save_history(messages)
            print("Сохранено. Пока!")
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

        # обычный чат
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        print("AI:", reply)


if __name__ == "__main__":
    chat()