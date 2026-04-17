import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_sentiment(text):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Analyze sentiment: positive, negative or neutral."},
            {"role": "user", "content": text}
        ]
    )

    return response.choices[0].message.content.strip()