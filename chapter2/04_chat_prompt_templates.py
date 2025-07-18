import os
import sys
# Add the parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import set_environment
set_environment()

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# IT’S BEST USED FOR SINGLE-TURN PROMPTS (I.E., ONE USER MESSAGE AT A TIME) OR STRUCTURED, SCRIPTED INTERACTIONS.
template = ChatPromptTemplate.from_messages([
    ("system", "You are a english to french translator."),
    ("user", "Translate this to French: {text}")
])

# Initialize the model
chat = ChatOpenAI(model="gpt-4o")
formatted_messages = template.format_messages(text="Hello, how are you?")
response = chat.invoke(formatted_messages)
print(response.content)

