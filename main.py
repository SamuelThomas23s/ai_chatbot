from openai import OpenAI
from config import API_KEY
import json
import os

client = OpenAI(api_key=API_KEY)

HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [{"role": "system", "content": "Ты полезный ассистент."}]

def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def chat():
    print("AI Chatbot с памятью + сохранением (exit для выхода)\n")

    messages = load_history()

    while True:
        user_input = input("Ты: ")

        if user_input.lower() == "exit":
            save_history(messages)
            print("История сохранена. Пока!")
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        save_history(messages)  # сохраняем после каждого ответа

        print("AI:", reply)


if __name__ == "__main__":
    chat()