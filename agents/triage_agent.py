import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# --- Placeholder Imports ---
# We haven't created these files yet, but we will.
# This code won't run until all agent files are created.
from . import bug_hunter_agent
from . import dev_agent
from . import qa_agent
# -------------------------

# --- 1. Define the Tools for the Triage Agent ---
# The Triage Agent's tools are the other agents.
# We wrap their 'run' functions in a @tool decorator.

@tool
def validate_bug_report(bug_description: str) -> str:
    """
    Use this tool FIRST to validate if a bug report is real.
    It runs an agent that inspects the website's code.
    Input is the original bug description.
    Output is a confirmation or denial of the bug.
    """
    print(f"\n--- [Triage Agent] Calling Bug-Hunter Agent ---")
    return bug_hunter_agent.run(bug_description)

@tool
def fix_bug(bug_description: str) -> str:
    """
    Use this tool SECOND, only after a bug has been validated.
    It runs a developer agent to read the code, write a fix, and apply it.
    Input is the original bug description.
    Output is a summary of the fix applied.
    """
    print(f"\n--- [Triage Agent] Calling Dev Agent ---")
    return dev_agent.run(bug_description)

@tool
def verify_fix(bug_description: str) -> str:
    """
    Use this tool LAST, after a fix has been applied.
    It runs a QA agent to verify that the bug is no longer present.
    Input is the original bug description (to know what to check).
    Output is a "PASS" or "FAIL" judgment.
    """
    print(f"\n--- [Triage Agent] Calling QA Agent (Agent-as-a-Judge) ---")
    return qa_agent.run(bug_description)


# --- 2. Define the Agent's "Constitution" (System Prompt) ---
# This prompt is the "brain" of our Triage Agent.
# It's a "coordinator" pattern 
# It defines the agent's persona, its tools, and its logic.
# This is a core concept from Day 1 and Day 3[cite: 38, 64, 2495].

prompt_template = """
You are the "Triage Agent," the project manager for a self-healing website system.
Your goal is to coordinate a team of specialist agents to fix bugs.

You must follow this strict, 3-step workflow:
1.  **VALIDATE:** First, you MUST use the `validate_bug_report` tool to confirm the bug is real.
2.  **FIX:** SECOND, *if and only if* the bug was validated, you MUST use the `fix_bug` tool to apply a patch.
3.  **VERIFY:** THIRD, *after* the fix is applied, you MUST use the `verify_fix` tool to confirm the fix worked.

Do not skip any steps. Report the final outcome of the entire process.
"""

# --- 3. Create the Agent ---

def create_triage_agent():
    """
    Factory function to create and return the Triage Agent executor.
    """
    print("Initializing Triage Agent...")
    
    # Use a powerful model for the "manager" agent
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    
    # Get the list of tools
    tools = [validate_bug_report, fix_bug, verify_fix]
    
    # Create the prompt from our template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_template),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    
    # Create the agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Create the agent executor (the runtime)
    # verbose=True gives us the "Observability Trace" (Day 4) [cite: 4322, 4340]
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    print("Triage Agent is ready.")
    return agent_executor

# --- 4. Define the `run` function for main.py ---
# We will create the agent once and reuse it.
triage_agent_executor = create_triage_agent()

def run(bug_report: str) -> dict:
    """
    The main entry point for the Triage Agent.
    """
    print(f"Triage Agent received report: '{bug_report}'")
    
    # Invoke the agent executor
    # We pass the bug report as the "input"
    response = triage_agent_executor.invoke({
        "input": bug_report
    })
    
    return response