import os
import sys
# Add the parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import set_environment
set_environment()

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

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


# To preserve the story, we can use a RunnablePassthrough to pass the story along
enhanced_chain = RunnablePassthrough.assign(
    story=story_chain # Add 'story' key with generated content. It is important to use word "story" as analysis_chain expects it.
).assign(analysis=analysis_chain) #  Add 'analysis' key with analysis of the story

# Execute the chain
result = enhanced_chain.invoke({"topic": "a rainy night"})

print(result.keys()) # Output: dict_keys(['topic', 'story', 'analysis'])

# Why use RunnablePassthrough?
# > It's a clean way to add intermediate outputs (like story) into the execution context.
# > Keeps the full input/output history without losing previous values.
# > Easily composable and declarative using LCEL (LangChain Expression Language).

# You can think of RunnablePassthrough.assign(...) like enriching a data record as it flows through a pipeline:

# [Start]
#   |
#   |  + Generate 'story' from topic → add it to the input
#   |  + Analyze 'story' → add 'analysis' to input
#   v
# [Final Output: topic + story + analysis]