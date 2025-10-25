import openai, os
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_gpt(prompt: str):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
