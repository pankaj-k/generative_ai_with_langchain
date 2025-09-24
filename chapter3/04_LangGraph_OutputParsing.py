# The output of a LLM is text. If you want it to be used in next steps of your graph, you need to parse it
# and convert it to a structured format, like a JSON, XML or even a simple key-value pair.
# This is called Output Parsing.

# Here we will make llm parse receipts from the shop and extract key information like total amount, date, items purchased etc.
# We will then use ouput parser to convert the output into a JSON format. LLM should do it if instructed but it
# will return a JSON string. 

from langchain.output_parsers import PydanticOutputParser
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END, Graph
import glob

from langsmith import utils
utils.tracing_is_enabled()
from langsmith import traceable

from pydantic import BaseModel

# Not using TypedDict here because we want to use PydanticOutputParser which works with Pydantic models.
# TypedDict is just a typing hint, it doesn't have any runtime behavior. Pydantic Can parse LLM JSON strings directly into a Python object.
# Pydantic models have validation and parsing capabilities at runtime. Runtime validation: ensures types and required fields are correct.
# Provides convenience methods: .dict(), .json(), .copy()
# Works directly with PydanticOutputParser in LangChain / LangGraph
# So we define a Pydantic model for the receipt data.
class ReceiptData(BaseModel):
    shop_name: str
    purchase_date: str
    purchase_price: float
    gst: float

# Load the receipts from text files
def load_receipts():
    receipts = []
    for filepath in glob.glob("receipts/*.txt"):
        with open(filepath, "r") as f:
            receipts.append(f.read())
    return receipts

