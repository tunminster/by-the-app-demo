import os
import openai

openai.api.key = os.environ.get('OPENAI_API_KEY')

training_data = [
    {"input": "Hi", "output" : "Hi there, how can i help you?"},
    {"input": "Yes. I want to cancel my credit card", "output": "Sure. I can help you with this."}

]

# Train the model
response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages= training_data,
    max_tokens=150,
    temperature=0.7,
    stop=None
)

print(response.choices[0].message['text'])