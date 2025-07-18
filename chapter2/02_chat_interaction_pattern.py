import os
import sys
# Add the parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import set_environment
set_environment()

from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

chat = ChatOpenAI(model="gpt-4o")

# BEST FOR MULTI-TURN CONVERSATIONS
messages = [SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="What is the capital of France?")]
response = chat.invoke(messages)
print(response.content)  # Output: Paris

# Add the assistant's reply to the conversation history
messages.append(AIMessage(response.content))

# Second turn: follow-up question
messages.append(HumanMessage(content="What is is population?"))
response = chat.invoke(messages)

print(response.content)  # Output: The population of Paris is approximately 2.1 million