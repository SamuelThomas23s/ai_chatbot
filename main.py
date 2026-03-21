from openai import OpenAI
from config import API_KEY

client = OpenAI(api_key=API_KEY)

def chat():
    print("AI Chatbot (напиши 'exit' чтобы выйти)\n")

    while True:
        user_input = input("Ты: ")

        if user_input.lower() == "exit":
            print("Пока!")
            break

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты полезный ассистент."},
                {"role": "user", "content": user_input}
            ]
        )

        reply = response.choices[0].message.content
        print("AI:", reply)

if __name__ == "__main__":
    chat()