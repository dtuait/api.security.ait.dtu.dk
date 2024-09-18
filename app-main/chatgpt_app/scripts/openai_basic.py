from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import json

class Step(BaseModel):
    explanation: str
    output: str

class MathReasoning(BaseModel):
    steps: list[Step]
    final_answer: str

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

def run():
    # Load environment variables
    env_path = '/usr/src/project/.devcontainer/.env'
    load_dotenv(dotenv_path=env_path)

    client = OpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")

    # Correct method to call chat completions
    completion = client.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Extract the event information."},
            {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
        ],
    )

    response_content = completion.choices[0].message["content"]

    # Print the raw response for debugging
    print("Response from OpenAI:", response_content)

    # Assuming the response contains a JSON-like string that matches CalendarEvent structure
    try:
        # Parse the response into a dict and then map it to CalendarEvent model
        event_data = json.loads(response_content)
        calendar_event = CalendarEvent(**event_data)
        print("Parsed Calendar Event:", calendar_event)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")

if __name__ == "__main__":
    run()
