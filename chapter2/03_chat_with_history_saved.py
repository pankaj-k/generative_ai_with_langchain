import os
import sys
# Add the parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import set_environment
set_environment()

import json
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Path to save conversation history
HISTORY_FILE = "chapter1/chat_history.json"

# Load existing history if present
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
            return [deserialize_message(m) for m in raw]
    else:
        return [SystemMessage(content="You are a helpful assistant.")]
    
# Serialize LangChain messages
def serialize_message(msg):
    return {"type": msg.type, "content": msg.content}

# Save history to disk
def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([serialize_message(m) for m in history], f, indent=2)

# Deserialize messages from JSON
def deserialize_message(msg):
    if msg["type"] == "system":
        return SystemMessage(content=msg["content"])
    elif msg["type"] == "human":
        return HumanMessage(content=msg["content"])
    elif msg["type"] == "ai":
        return AIMessage(content=msg["content"])
    else:
        raise ValueError(f"Unknown message type: {msg['type']}")
    
# Initialize model
chat = ChatOpenAI(model="gpt-4o")

# Load previous chat if available
messages = load_history()

print("💬 Chat started. Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    
    # Add user message to history
    messages.append(HumanMessage(content=user_input))
    
    # Get response from model
    response = chat.invoke(messages)
    
    # Add assistant's reply to history
    messages.append(AIMessage(response.content))
    
    # Print the response
    print(f"🤖 Assistant: {response.content}\n")
    
    save_history(messages)