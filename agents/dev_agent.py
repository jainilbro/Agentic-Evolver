import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# --- 1. Import This Agent's Specific Tools ---
# This agent gets the "powerful" tools: read, write, and update memory.
from tools.file_manager import read_css_file, write_css_file, update_procedural_memory

# --- 2. Wrap the Tools for the Agent ---
# We make the tools available for this agent to use.

@tool
def get_current_css_code() -> str:
    """
    Reads and returns the entire content of the 'style.css' file.
    Use this tool FIRST to understand the current state of the code.
    """
    print(f"\n--- [Dev Agent Tool] Reading from style.css ---")
    return read_css_file()

@tool
def apply_css_fix(new_css_content: str) -> str:
    """
    Overwrites the 'style.css' file with new, corrected content.
    Use this tool SECOND, after you have generated the complete, fixed CSS.
    The 'new_css_content' argument must be a string containing the ENTIRE
    contents of the CSS file, not just the changed part.
    """
    print(f"\n--- [Dev Agent Tool] Writing to style.css ---")
    return write_css_file(new_css_content)

@tool
def save_fix_to_memory(bug_description: str, fix_applied: str) -> str:
    """
    Use this tool LAST, after successfully applying a fix.
    This saves the solution to the agent's long-term procedural memory.
    Args:
        bug_description: The original bug report (e.g., "button is blue").
        fix_applied: A short description of the fix (e.g., "Changed .contact-button background-color to #ff0000").
    """
    print(f"\n--- [Dev Agent Tool] Writing to procedural_memory.json ---")
    return update_procedural_memory(bug_description, fix_applied)

# --- 3. Define the Agent's "Constitution" (System Prompt) ---
# This is a complex prompt for our "coder" agent.
prompt_template = """
You are an expert "Dev Agent," an autonomous front-end developer.
Your goal is to fix bugs in the website's CSS.

You have one core task: READ the code, WRITE the fix, and REMEMBER the fix.
You *must* call all three tools in sequence to complete your job.

Workflow:
1.  **READ:** You MUST start by calling `get_current_css_code` to read the entire `style.css` file.
2.  **WRITE:** Based on the user's bug report and the code you just read, you MUST generate the new,
    complete CSS content with the bug fixed. Then you MUST call `apply_css_fix` with this new content.
3.  **REMEMBER:** After the fix is successfully applied, you MUST call `save_fix_to_memory`
    to record what you did.

This is not optional. You must follow all three steps.
Do not stop until `save_fix_to_memory` has been called.

EXAMPLE:
- Bug Report: "The contact button is blue, it should be red."
- Step 1: Call `get_current_css_code()`.
- Step 2: (Receive code) -> Generate new code with `background-color: #ff0000;` -> Call `apply_css_fix(...)`.
- Step 3: (Receive success) -> Call `save_fix_to_memory(...)`.

EXAMPLE 2:
- Bug Report: "The contact button is red, it should be blue."
- Step 1: Call `get_current_css_code()`.
- Step 2: (Receive code) -> Generate new code with `background-color: #007bff;` -> Call `apply_css_fix(...)`.
- Step 3: (Receive success) -> Call `save_fix_to_memory(...)`.

IMPORTANT: Your final, final response to me (the Triage Agent) MUST be a single, short sentence: "FIX APPLIED."
Do not say anything else. Just "FIX APPLIED."
"""

# --- 4. Create the Agent ---

def create_dev_agent():
    """
    Factory function to create and return the Dev Agent executor.
    """
    print("Initializing Dev Agent...")
    
    # We use a powerful model for our "coder" agent
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash") # Using flash as you suggested
    
    tools = [get_current_css_code, apply_css_fix, save_fix_to_memory]
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_template),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # [cite_start]verbose=True gives us the "Observability Trace" (Day 4) [cite: 2196-2198, 2213]
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    print("Dev Agent is ready.")
    return agent_executor

# --- 5. Define the `run` function for the Triage Agent ---
dev_agent_executor = create_dev_agent()

def run(bug_description: str) -> str:
    """
    The main entry point for the Dev Agent.
    """
    print(f"Dev Agent received report: '{bug_description}'")
    
    response = dev_agent_executor.invoke({
        "input": bug_description
    })
    
    # Return just the final output string
    return response['output']