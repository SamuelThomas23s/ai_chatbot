from openai import OpenAI
from config import API_KEY

client = OpenAI(api_key=API_KEY)

def chat():
    print("AI Chatbot с памятью (напиши 'exit' чтобы выйти)\n")

    # 🧠 История сообщений
    messages = [
        {"role": "system", "content": "Ты полезный ассистент."}
    ]

    while True:
        user_input = input("Ты: ")

        if user_input.lower() == "exit":
            print("Пока!")
            break

        # Добавляем сообщение пользователя в историю
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = response.choices[0].message.content

        # Добавляем ответ ИИ в историю
        messages.append({"role": "assistant", "content": reply})

        print("AI:", reply)


if __name__ == "__main__":
    chat()