from openai import OpenAI
import os
# from dotenv import load_dotenv
from function_schema import tools
# Load environment variables from .env file
# load_dotenv()

# Access the variables

client = OpenAI()


assistant = client.beta.assistants.create(
    name="Assistant",
    instructions="You are Bigquery SQL generator assistant.. And help me build queries for our DW to analyse multiple queries.",
    tools=tools,
    model="gpt-4o",
)

print(assistant.id)