import os
import sys
# Add the parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import set_environment
set_environment()

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Initialize the model
llm = ChatOpenAI(model="gpt-4o")

# First chain generates a story
prompt = ChatPromptTemplate.from_template("Write a short story about {topic}")
output_parser = StrOutputParser()

# Chain them together using LCEL
story_chain = prompt | llm | output_parser

# Second chain analyses the story
analysis_prompt = ChatPromptTemplate.from_template("Analyze the following story's mood: {story}")

# Chain for analysis
analysis_chain = analysis_prompt | llm | output_parser

# combine both chains   
story_with_analysis_chain = story_chain | analysis_chain

# Execute the workflow with a single call.
story_analysis = story_with_analysis_chain.invoke({"topic": "a rainy night"})
print("\nAnalysis:", story_analysis)

# The output of the first chain is stored in story parameter of the second chain.
# The story however is lost in the process. How to preserve it? That is the next example.