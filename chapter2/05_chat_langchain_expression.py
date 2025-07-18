import os
import sys
# Add the parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import set_environment
set_environment()

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Create components
prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
# Initialize the model
chat = ChatOpenAI(model="gpt-4o")
output_parser = StrOutputParser()

# Chain them together using LCEL
chain = prompt | chat | output_parser

# Execute the workflow with a single call.
result = chain.invoke({"topic": "programming"})
print(result)  # Output: A joke about programming