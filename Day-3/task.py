# Day-3: LearnPath AI Conversation and Evaluation

# Install packages:
# pip install -U langchain langchain-groq

import csv
from pathlib import Path

from google.colab import userdata
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_agent


# API Configuration
api_key = userdata.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing. Add it in Colab Secrets.")

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.4,
    api_key=api_key
)

print("LearnPath AI connected successfully!")


# System Instructions
SYSTEM = """
ROLE:
You are LearnPath AI, a friendly study assistant.

YOU CAN HELP WITH:
- Creating daily and weekly study plans.
- Explaining difficult academic topics.
- Preparing students for examinations.
- Managing study time.
- Suggesting revision strategies.
- Improving learning progress.

RULES:
- Give simple explanations.
- Create realistic study schedules.
- Focus on difficult subjects.
- Encourage regular revision.
- Ask questions when information is missing.

FORMAT:
Be friendly, supportive and concise.
Reply in English or Telugu according to the student's language.
"""


# Create Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    MessagesPlaceholder("history"),
    ("human", "{question}")
])

chain = prompt | llm | StrOutputParser()

print("LearnPath AI chain created successfully!")


# Conversation History
history = []


def ask(question):

    answer = chain.invoke({
        "history": history,
        "question": question
    })

    history.extend([
        ("human", question),
        ("ai", answer)
    ])

    return answer


# Conversation Demo
def demo_chat():

    print("\n--- LearnPath AI Conversation Demo ---")

    question1 = "I am preparing for Python and DBMS."

    print("\nStudent:", question1)
    print("AI:", ask(question1))

    question2 = "Which subjects am I preparing for?"

    print("\nStudent:", question2)
    print("AI:", ask(question2))


demo_chat()


# Create Evaluation Dataset
test_data = [
    ["question", "expected_keyword"],
    ["Create a Python study plan", "Python"],
    ["How can I manage my study time?", "time"],
    ["Why is revision important?", "revision"],
    ["How can I improve coding skills?", "practice"]
]


with open(
    "learnpath_test.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)
    writer.writerows(test_data)

print("\nTest cases created successfully!")


# Evaluation Function
def run_tests(path="learnpath_test.csv"):

    csv_path = Path(path)

    if not csv_path.exists():

        print("Test file not found!")
        return

    with csv_path.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        rows = list(csv.DictReader(file))

    if not rows:

        print("No test cases found!")
        return

    passed = 0

    print("\n--- Evaluation Results ---")

    for row in rows:

        question = row["question"]
        expected = row["expected_keyword"]

        answer = chain.invoke({
            "history": [],
            "question": question
        })

        success = expected.lower() in answer.lower()

        if success:
            passed += 1

        print(
            ("PASS" if success else "FAIL"),
            "|",
            question,
            "->",
            answer[:100].replace("\n", " ")
        )

    percentage = (passed / len(rows)) * 100

    print(
        f"\n{passed}/{len(rows)} tests passed "
        f"({percentage:.0f}%)."
    )


run_tests()


# Agent Demonstration
def agent_demo():

    print("\n--- LearnPath AI Agent Demo ---")

    agent = create_agent(
        model=llm,
        tools=[],
        system_prompt=SYSTEM
    )

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": (
                    "Create a simple 2-hour daily study plan "
                    "for Python and DBMS."
                )
            }
        ]
    })

    print(result["messages"][-1].content)


agent_demo()
