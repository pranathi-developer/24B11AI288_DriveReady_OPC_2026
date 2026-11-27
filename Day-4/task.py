
# Day-4: Sweet Crumbs AI Agent
# Tools, Function Calling, Pydantic and Google Sheets

# Install required packages in Google Colab:
# !pip install -q langchain langchain-groq gspread pydantic

import os
import gspread

from typing import Literal, Optional
from pydantic import BaseModel, Field
from google.colab import userdata, auth
from google.auth import default

from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent


# --------------------------------------------------
# 1. API CONFIGURATION
# --------------------------------------------------

api_key = userdata.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("Please add GROQ_API_KEY in Colab Secrets.")

os.environ["GROQ_API_KEY"] = api_key

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.2,
    max_retries=3
)

print("Groq model connected successfully!")


# --------------------------------------------------
# 2. GOOGLE SHEETS CONFIGURATION
# --------------------------------------------------

auth.authenticate_user()

credentials, _ = default()
gc = gspread.authorize(credentials)

SHEET_NAME = "Sweet Crumbs Orders"

try:
    spreadsheet = gc.open(SHEET_NAME)
    worksheet = spreadsheet.sheet1
    print("Existing Google Sheet opened.")

except gspread.SpreadsheetNotFound:
    spreadsheet = gc.create(SHEET_NAME)
    worksheet = spreadsheet.sheet1

    worksheet.append_row([
        "Customer Name",
        "Item",
        "Quantity",
        "Pickup Date",
        "Eggless",
        "Total Price"
    ])

    print("New Google Sheet created.")

print("Google Sheet URL:", spreadsheet.url)


# --------------------------------------------------
# 3. BAKERY DATA
# --------------------------------------------------

MENU = {
    "plum cake": 500,
    "chocolate cake": 650,
    "cupcake": 80
}

OPENING_HOURS = {
    "monday": "9 AM to 8 PM",
    "tuesday": "9 AM to 8 PM",
    "wednesday": "9 AM to 8 PM",
    "thursday": "9 AM to 8 PM",
    "friday": "9 AM to 8 PM",
    "saturday": "9 AM to 8 PM",
    "sunday": "10 AM to 6 PM"
}


# --------------------------------------------------
# 4. PYDANTIC ORDER MODEL
# --------------------------------------------------

class Order(BaseModel):
    """Validate customer bakery order information."""

    name: str = Field(description="Customer first name")

    item: Literal[
        "plum cake",
        "chocolate cake",
        "cupcake"
    ] = Field(description="Selected bakery item")

    qty: int = Field(
        description="Required quantity",
        ge=1
    )

    date: str = Field(
        description="Customer pickup date"
    )

    eggless: bool = Field(
        description="Whether eggless cakes are required"
    )


# Optional fields help identify missing details
# before an order is saved.

class OrderDraft(BaseModel):
    name: Optional[str] = None
    item: Optional[str] = None
    qty: Optional[int] = None
    date: Optional[str] = None
    eggless: Optional[bool] = None


# Structured output demonstration
def extract_order_details(message):

    extractor = llm.with_structured_output(OrderDraft)

    return extractor.invoke(
        "Extract the order information from this message. "
        "Do not invent missing details. "
        "Use null for information that is not provided.\n\n"
        + message
    )


print("\nPydantic Order model created successfully!")


# --------------------------------------------------
# 5. TOOL 1: GET PRICE
# --------------------------------------------------

@tool
def get_price(item: str, qty: int = 1) -> str:
    """Get the total bakery price in rupees.

    Args:
        item: Bakery item name.
        qty: Number of items required.
    """

    item = item.lower().strip()

    if item not in MENU:
        return (
            f"{item} is unavailable. "
            f"Available items: {', '.join(MENU.keys())}"
        )

    if qty < 1:
        return "Quantity must be at least 1."

    total = MENU[item] * qty

    return f"{qty} x {item} = Rs {total}"


# --------------------------------------------------
# 6. TOOL 2: CHECK OPENING HOURS
# --------------------------------------------------

@tool
def is_open(day: str) -> str:
    """Check bakery opening hours for a weekday.

    Args:
        day: Day of the week.
    """

    day = day.lower().strip()

    hours = OPENING_HOURS.get(day)

    if hours:
        return f"Bakery is open on {day}: {hours}"

    return "Please provide a valid day of the week."


# --------------------------------------------------
# 7. TOOL 3: SAVE ORDER
# --------------------------------------------------

@tool
def log_order(
    name: str,
    item: str,
    qty: int,
    date: str,
    eggless: bool
) -> str:
    """Save a confirmed customer order to Google Sheets.

    Use this tool only when the customer has provided
    name, item, quantity and pickup date.
    """

    try:
        order = Order(
            name=name,
            item=item.lower().strip(),
            qty=qty,
            date=date,
            eggless=eggless
        )

    except Exception as error:
        return f"Order validation failed: {error}"

    total = MENU[order.item] * order.qty

    try:
        worksheet.append_row([
            order.name,
            order.item,
            order.qty,
            order.date,
            "Yes" if order.eggless else "No",
            total
        ])

    except Exception as error:
        return f"Unable to save order: {error}"

    return (
        f"Order successfully saved! "
        f"{order.qty} {order.item} for {order.name}. "
        f"Pickup date: {order.date}. "
        f"Total: Rs {total}."
    )


print("All three tools registered successfully!")


# --------------------------------------------------
# 8. CREATE AI AGENT
# --------------------------------------------------

SYSTEM_PROMPT = """
You are Sweet Crumbs, a friendly bakery ordering assistant.

BUSINESS INFORMATION:
- Custom cake orders require 24 hours' notice.
- Eggless options are available for cakes.
- Bakery products include plum cake, chocolate cake
  and cupcakes.

RULES:
1. Always use get_price to calculate prices.
2. Always use is_open to check opening hours.
3. Never invent prices or business timings.
4. Before saving an order, collect the customer's
   name, item, quantity and pickup date.
5. Ask questions if any required information is missing.
6. Use log_order only after all required details
   are available and the customer confirms the order.
7. Read the saved order and total price back to the customer.
8. Keep responses short and friendly.
9. Respond in English or Telugu according to the customer.
"""

agent = create_agent(
    model=llm,
    tools=[
        get_price,
        is_open,
        log_order
    ],
    system_prompt=SYSTEM_PROMPT
)

print("Sweet Crumbs AI Agent created successfully!")


# --------------------------------------------------
# 9. CHAT FUNCTION WITH MEMORY
# --------------------------------------------------

chat_history = []


def chat(user_message):

    global chat_history

    try:
        result = agent.invoke({
            "messages": chat_history + [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        })

        chat_history = result["messages"]

        return chat_history[-1].content

    except Exception as error:

        print("Agent error:", error)

        return "Sorry, please try again."


# --------------------------------------------------
# 10. TEST THE AGENT
# --------------------------------------------------

print("\n--- Sweet Crumbs AI Demo ---")

question1 = (
    "Are you open on Sunday? "
    "What is the price of 2 chocolate cakes?"
)

print("\nCustomer:", question1)
print("Assistant:", chat(question1))


question2 = (
    "My name is Ravi. I need 2 eggless "
    "chocolate cakes for 24 Dec."
)

print("\nCustomer:", question2)
print("Assistant:", chat(question2))


# --------------------------------------------------
# 11. DISPLAY AGENT TRACE
# --------------------------------------------------

print("\n--- Agent Execution Trace ---")

for message in chat_history:
    message.pretty_print()


# --------------------------------------------------
# 12. STRUCTURED OUTPUT TESTS
# --------------------------------------------------

test_messages = [
    "I am Ravi. I need 2 plum cakes for Sunday.",
    "My name is Anu. I want 5 cupcakes tomorrow.",
    "I need one chocolate cake.",
    "Book 3 eggless cupcakes for Saturday.",
    "I am Sravani. I need 2 chocolate cakes."
]

print("\n--- Structured Output Testing ---")

for message in test_messages:

    print("\nInput:", message)

    try:
        structured_data = extract_order_details(message)

        print("Extracted Data:")
        print(structured_data.model_dump())

    except Exception as error:
        print("Extraction error:", error)


print("\nDay-4 task completed successfully!")
