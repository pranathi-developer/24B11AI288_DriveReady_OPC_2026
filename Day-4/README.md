::writing{variant="document" id="84262"}
# Day-4: Sweet Crumbs AI Agent

## Project Description

This project develops an intelligent bakery ordering assistant using Generative AI, LangChain and Groq API.

The AI agent helps customers check bakery prices, find opening hours, place orders and save order details automatically in Google Sheets.

## Technologies Used

- Python
- LangChain
- Groq API
- Pydantic
- Google Sheets
- Gspread
- Google Colab

## Features

- AI agent with multiple tools.
- Function calling using LangChain.
- Bakery price calculation.
- Opening hours verification.
- Structured output using Pydantic.
- Customer order validation.
- Automatic order storage in Google Sheets.
- Conversation history and agent execution tracing.
- Error handling for invalid orders.

## Tools Implemented

1. **get_price:** Calculates the total price of bakery items.
2. **is_open:** Checks bakery opening hours.
3. **log_order:** Validates and saves customer orders to Google Sheets.

## Installation

Install the required packages:

```bash
pip install -U langchain langchain-groq gspread pydantic
```

## API Key Setup

1. Open Google Colab.
2. Add your Groq API key in Colab Secrets.
3. Enable access to the key.
4. Authorize Google account access for Google Sheets.

## Execution

1. Open `task.py` in Google Colab.
2. Install the required packages.
3. Configure the Groq API key.
4. Authorize Google Sheets.
5. Run the Python code.
6. Test the AI assistant with customer questions.
7. Check the Google Sheet for saved orders.

## Expected Output

- AI-generated customer responses.
- Bakery price calculations.
- Opening hours information.
- Structured customer order details.
- Validated orders.
- Automatically updated Google Sheets.

## Conclusion



