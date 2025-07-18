# Uses TypeDict which is similar to Struct in C. You have a class like structure with named fields of specific types.
# from typing import TypedDict

# class User(TypedDict):
#     name: str
#     age: int

# u: User = {"name": "Alice", "age": 30}

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END, Graph

class JobApplicationState(TypedDict):
    job_description: str
    is_suitable: bool
    application: str

def analyze_job_description(state):
    print("...Analyzing job description...")
    return {"is_suitable":len(state["job_description"]) > 100}

def generate_application(state):
    print("...Generating application...")
    return {"application": "some_fake_application"}

builder = StateGraph(JobApplicationState)
builder.add_node("analyze_job_description", analyze_job_description)
builder.add_node("generate_application", generate_application)
builder.add_edge(START, "analyze_job_description")
builder.add_edge("analyze_job_description", "generate_application")
builder.add_edge("generate_application", END)
graph = builder.compile()

res = graph.invoke({"job_description":"fake_jd"}) # Automatically starts at the special START node in the LangGraph.
print(res)

# You initialize the state with: {"job_description": "fake_jd"}
    
# The state is passed to the first node: analyze_job_description(state)
# def analyze_job_description(state):
#     return {"is_suitable": len(state["job_description"]) > 100}

# This returns a partial update:
# {"is_suitable": False}
# (since the length of "fake_jd" is less than 100)


# Then it goes to generate_application(state) and returns:
# {"application": "some_fake_application"}

# After this, final state becomes:
# {
#     "job_description": "fake_jd",
#     "is_suitable": False,
#     "application": "some_fake_application"
# }

# So what happens at END?
# In LangGraph, the END node is a special terminal state.
# When the graph reaches the END node, it stops execution and returns the current state dictionary as the result of the invoke()
# After generate_application runs, the graph terminates — and the final state (a dict with keys like job_description, is_suitable, and application) is returned to you.
# So when you do:res = graph.invoke({"job_description":"fake_jd"})
# print(res)
# You get:
# {
#   "job_description": "fake_jd",
#   "is_suitable": False,  # computed during analyze_job_description
#   "application": "some_fake_application"  # added in generate_application
# }

# Summary:
# END means “we're done”.
# No more nodes are executed.
# Whatever is in the state at that moment is returned by invoke().