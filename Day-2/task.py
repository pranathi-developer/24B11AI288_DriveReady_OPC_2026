# Day-2: LearnPath AI Study Assistant

# Install packages:
# pip install openai ipywidgets

from openai import OpenAI
from google.colab import userdata
import json
import time
from functools import wraps

# API Configuration
api_key = userdata.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("Please add GROQ_API_KEY in Colab Secrets.")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

MODEL_NAME = "openai/gpt-oss-120b"

print("LearnPath AI connected successfully!")


# Student Information
STUDENT_PROFILE = {
    "name": "Anu",
    "subjects": ["Python", "DBMS", "DSA"],
    "study_hours": 2,
    "weak_topics": ["Recursion", "SQL Joins"],
    "goal": "Prepare for semester examinations"
}


# System Prompt
SYSTEM_PROMPT = f"""
You are LearnPath AI, a helpful study assistant.

Student Profile:
{json.dumps(STUDENT_PROFILE, indent=2)}

Your responsibilities:
- Create study timetables.
- Explain difficult concepts.
- Suggest revision methods.
- Help students manage study time.
- Provide coding practice suggestions.

Give simple and beginner-friendly answers.
"""


# Function to classify user intent
def classify_intent(user_input):

    prompt = f"""
    Classify the student's request into one category:
    study_plan, concept_help, revision,
    time_management, progress_tracking.

    Student request: {user_input}

    Return only the category.
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# Extract student information
def extract_student_info(user_input):

    prompt = f"""
    Extract student information from this message.

    Return valid JSON with these keys:
    student_name, subjects, exam_date,
    study_hours, weak_topics, priority.

    Use null or empty lists for missing details.

    Message: {user_input}
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content


# Execution time decorator
def measure_time(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        start = time.time()

        print(f"Executing {func.__name__}...")

        result = func(*args, **kwargs)

        end = time.time()

        print(f"Completed in {end-start:.2f} seconds")

        return result

    return wrapper


# LearnPath AI Agent
class LearnPathAgent:

    def __init__(self):

        self.history = []
        self.max_turns = 10

    @measure_time
    def chat(self, user_input):

        intent = classify_intent(user_input)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        messages.extend(self.history)

        messages.append({
            "role": "user",
            "content": f"Intent: {intent}\nQuestion: {user_input}"
        })

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.5
        )

        answer = response.choices[0].message.content

        self.history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": answer}
        ])

        self.history = self.history[-self.max_turns:]

        return answer


# Create agent
agent = LearnPathAgent()

print("LearnPath AI Agent created successfully!")


# Test conversation
answer1 = agent.chat(
    "I am preparing for Python and DBMS examinations."
)

print("\nLearnPath AI:")
print(answer1)

answer2 = agent.chat(
    "Which subjects am I preparing for?"
)

print("\nLearnPath AI:")
print(answer2)


# Interactive Chat Interface
import ipywidgets as widgets
from IPython.display import display

chat_input = widgets.Text(
    placeholder="Ask your study question...",
    description="You:"
)

send_button = widgets.Button(
    description="Send",
    button_style="success"
)

chat_output = widgets.Output()


def send_message(button):

    question = chat_input.value.strip()

    if question:

        with chat_output:

            print("You:", question)

            response = agent.chat(question)

            print("\nLearnPath AI:", response)
            print("-" * 40)

        chat_input.value = ""


send_button.on_click(send_message)

display(chat_input, send_button, chat_output)
