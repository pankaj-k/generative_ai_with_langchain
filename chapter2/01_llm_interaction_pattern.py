import os
import sys
# Add the parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import set_environment
set_environment()

from langchain_openai import OpenAI
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.llms import FakeListLLM

# Initialize OpenAI and Gemini clients
openai_llm = OpenAI()
gemini_pro = GoogleGenerativeAI(model = "gemini-1.5-pro")

response = openai_llm.invoke("Tell me a joke about light bulbs!")
print("\nOpenAI Response:", response)

response = gemini_pro.invoke("Tell me a joke about light bulbs!")
print("\nGemini Response:", response)

# Create a fake LLM that always returns the same response
fake_llm = FakeListLLM(responses=["Hello"])
result = fake_llm.invoke("Any input will return Hello")
print(result) # Output: Hello