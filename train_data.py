import os
import openai

openai.api_key = os.environ.get('OPENAI_API_KEY')

training_data = [
    {"role": "system", "content": "Hi"},
    {"role": "user", "content": "Hi there, how can I help you?"},
    {"role": "user", "content": "Yes. I want to cancel my credit card"},
    {"role": "system", "content": "Sure. I can help you with this."}
]

# Use ChatCompletion.create for a conversation-like interaction
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=training_data,
    max_tokens=150,
    temperature=0.7,
    stop=None
)

print(response.choices[0].message['content'])
