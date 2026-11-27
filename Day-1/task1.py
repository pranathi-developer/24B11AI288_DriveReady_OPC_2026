
import os
from groq import Groq
from google.colab import userdata

# Load API Key
api_key = userdata.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("Please add GROQ_API_KEY in Colab Secrets.")

# Initialize Groq Client
client = Groq(api_key=api_key)

# System Prompt
SYSTEM_PROMPT = """
You are a helpful customer support assistant
for Sunrise Bake House.

Your responsibilities:
1. Answer customer questions.
2. Explain available bakery services.
3. Provide cake ordering information.
4. Help customers with their queries.

Guidelines:
- Be polite and friendly.
- Give simple answers.
- Do not invent prices or availability.
- Keep responses short and clear.
"""

# Function to get AI response
def customer_support(message):

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

# Test the assistant
print("Welcome to Sunrise Bake House!")

question = "Do you provide eggless cakes?"

answer = customer_support(question)

print("\nCustomer:", question)
print("AI Assistant:", answer)

# Multiple customer questions
questions = [
    "How can I order a birthday cake?",
    "How early should I place a custom cake order?",
    "Do you provide fresh bakery products?"
]

print("\n--- Customer Support Demo ---")

for question in questions:
    print("\nCustomer:", question)
    print("Assistant:", customer_support(question))

print("\nCustomer Support Assistant completed successfully!")
