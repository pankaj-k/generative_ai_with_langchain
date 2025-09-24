# LangGraph state is a dictionary of key-value pairs.
# At every superstep (think: a graph step), nodes may write to one or more keys in the state.
# If multiple nodes write to the same key, or if a node writes to a key multiple times over time, 
# LangGraph uses a reducer function to decide how to combine the old value with the new one.

# Default Reducer: reduce.replace
# This is the default. It just overwrites the old value with the new one.
# state = {"messages": ["Hi"]}
# # Node writes new value:
# new_value = ["How are you?"]
# # Reducer result = new_value

# No accumulation — just replacement.

# Built-in Reducer: add_messages
# LangGraph includes a special reducer for accumulating messages, useful for LLM-based agents.
# from langgraph.graph import StateGraph
# from langgraph.reducers import add_messages
# This reducer appends new messages to the existing list.

from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, add_messages, START, END
from langchain.chat_models import ChatOpenAI

# SystemMessage → role: "system" in OpenAI API.
# HumanMessage → role: "user" in OpenAI API. Provides user input. Sets the behavior of the assistant.
# AIMessage → role: "assistant" in OpenAI API. Used to append prior LLM outputs.

from langchain.schema import HumanMessage, AIMessage, BaseMessage, SystemMessage
from typing_extensions import TypedDict, List
from typing import Annotated

from langsmith import utils
utils.tracing_is_enabled()

from langsmith import traceable

# https://ploomber.io/blog/presidio/
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4", temperature=0) 
# Run this in powershell: $env:OPENAI_API_KEY = "sk-..."
# LangChain will automatically pick up OPENAI_API_KEY from the environment.

class ErrorLogState(TypedDict):
    error_log : str
    category : str
    notification_mode : str
    messages: Annotated[list[AnyMessage], add_messages]
    system_message: str

@traceable(run_type="retriever")
def extract_error_category(state):
    print("...Extracting error log...")
    raw_category  = state["error_log"].split(":")[0].strip()

    if raw_category == "INFO":
        return {"category": "low", "notification_mode": "none"}
    elif raw_category == "WARNING":
        return {"category": "moderate", "notification_mode": "email"}
    elif raw_category == "ERROR":
        return {"category": "high", "notification_mode": "sms"}
    elif raw_category in ["CRITICAL", "FATAL"]:
        return {"category": "critical", "notification_mode": "pager"}
    elif raw_category == "DEBUG":
        return {"category": "dev", "notification_mode": "log"}
    else:
        return {"category": "unknown", "notification_mode": "log"}

@traceable(run_type="retriever")
def remove_sensitive_info(state):
    print("...Removing sensitive info using Presidio...")
    
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    text = state.get("error_log", "")

    # Analyze PII entities in the text
    results = analyzer.analyze(text=text, entities=[], language="en")

    # Anonymize detected entities
    anonymized_text = anonymizer.anonymize(text=text, analyzer_results=results).text

    state["error_log"] = anonymized_text
    return state

@traceable(run_type="retriever")
def create_context_for_llm(state):
    print("...Creating context for LLM...")
    system_message = state["system_message"]

    # Create a context message for the LLM
    context_message = f"Error Category: {state['category']}\n"
    context_message += f"Notification Mode: {state['notification_mode']}\n"
    context_message += f"Error Log: {state['error_log']}\n"

    # Return state update with new message
    # LangGraph's reducer handle the message addition automatically 
    # if you've configured your graph state with the proper reducer for the messages field. In your case, it's `add_messages`.
    # This is a Partial State Update approach. Only returns the fields you want to change. 
    # LangGraph will automatically merge this with the existing state.

    # You can do this also. Full State Update
    # return {
    #     **state,
    #     "messages": updated_messages
    # }
    # This preserves ALL existing state fields and only updates the messages field. 
    # It's like saying "keep everything the same, but change just the messages."
    # Why use **state?
    # Explicit control: You're explicitly saying "I want to keep all existing state data"
    # Safety: Ensures no state fields are accidentally lost if LangGraph's merging behavior changes
    # Clarity: Makes it obvious you're updating the entire state, not just returning partial updates

    return {
        "messages": [SystemMessage(content=system_message),HumanMessage(content=context_message)]
    }

@traceable(run_type="retriever")
def llm_log_error_analysis(state):
    print("...Analysing error with LLM ...")
    
    # Call the LLM with the context message
    # Call the actual LLM on collected messages
    response = llm.invoke(state["messages"])
    # Return state update with new message
    return {
        "messages": [AIMessage(content=response.content)]
    }

@traceable(run_type="retriever")
def send_notification(state):
    print("...Sending notification...")
    
    # Simulating sending a notification
    if state["notification_mode"] == "none":
        print("No notification needed.")
    else:
        print(f"Notification sent via {state['notification_mode']}.")

# 2. Create the graph with the typed state
builder = StateGraph(ErrorLogState)


builder.add_node("extract_error_category", extract_error_category)
builder.add_node("remove_sensitive_info", remove_sensitive_info)
builder.add_node("create_context_for_llm", create_context_for_llm)
builder.add_node("llm_log_error_analysis", llm_log_error_analysis)
builder.add_node("send_notification", send_notification)

# 3. Add edges between nodes
builder.add_edge(START, "extract_error_category")
builder.add_edge("extract_error_category", "remove_sensitive_info")
builder.add_edge("remove_sensitive_info", "create_context_for_llm") 
builder.add_edge("create_context_for_llm", "llm_log_error_analysis")
builder.add_edge("llm_log_error_analysis", "send_notification")
builder.add_edge("send_notification", END)

graph = builder.compile()

# 4. Invoke the graph with initial state
initial_state: ErrorLogState = {
    "error_log": """ERROR:logstash.agent Failed to execute action {:action=>LogStash::PipelineAction::Create/pipeline_id:main, :exception=>"LogStash::ConfigurationError", :message=>"Expected one of [ \t\r\n], \"#\", \"{\" at line 2, column 11 (byte 19) after input{\r\nnpath ", :backtrace=>["C:/logstash-8.1.0/logstash-core/lib/logstash/compiler.rb:32:in `compile_imperative'", "org/logstash/execution/AbstractPipelineExt.java:189:in `initialize'", "org/logstash/execution/JavaBasePipelineExt.java:72:in `initialize'", "C:/logstash-8.1.0/logstash-core/lib/logstash/java_pipeline.rb:47:in `initialize'", "C:/logstash-8.1.0/logstash-core/lib/logstash/pipeline_action/create.rb:50:in `execute'", "C:/logstash-8.1.0/logstash-core/lib/logstash/agent.rb:376:in `block in converge_state'"]}""",
    "category": "",  # placeholder, will be updated
    "notification_mode": "",  # placeholder, will be updated
    "messages": [],
    "system_message": "You are a technical assistant. When given an error log, always respond with two sections: 'Analysis' and 'Fix'."
}

res = graph.invoke(initial_state)
print(res)