import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# --- 1. Import This Agent's Specific Tools ---
# GIVE THE QA AGENT THE NEW "EYES"
from tools.web_inspector import get_element_color, get_html_content

# --- 2. Wrap the Tools for the Agent ---
@tool
def read_html_file() -> str:
    """
    Reads and returns the entire content of the 'index.html' file.
    Use this tool FIRST to inspect the HTML and find the
    correct CSS selector for a given element.
    """
    print(f"\n--- [QA Agent Tool] Reading index.html ---")
    return get_html_content()

@tool
def verify_element_color(selector_text: str) -> str:
    """
    Finds a specific CSS rule by its selector (e.g., '.contact-button')
    and returns its 'background-color' property.
    Use this tool SECOND, *after* you have found the selector.
    """
    print(f"\n--- [QA Agent Tool] Verifying CSS for: {selector_text} ---")
    return get_element_color(selector_text)


# --- 3. Define the Agent's "Constitution" (System Prompt) ---
# This is the new, upgraded v2 prompt for the "Agent-as-a-Judge"
prompt_template = """
You are a "QA Agent" (an "Agent-as-a-Judge"). Your one and only job is to
verify if a bug fix was successful.

You will be given the original bug report (e.g., "button was blue, should be red").
This tells you the *INTENDED_STATE* (it "should be red").

You MUST use a 2-step process to find the *ACTUAL_STATE*:
1.  **FIND SELECTOR:** The user's report is in plain English (e.g., "Contact us button").
    You MUST call the `read_html_file` tool first to get the site's HTML.
    Then, you must analyze this HTML to find the *exact* CSS selector for the element the user is describing.
2.  **INSPECT COLOR:** After you have the selector, you MUST call the `verify_element_color` tool with that selector.

Finally, compare the *ACTUAL_STATE* (from the tool) with the *INTENDED_STATE* (from the bug report).
-   If they match (e.g., bug says "should be red" and tool finds "#ff0000"), the fix is a success. Report: "PASS. [Your rationale]."
-   If they do *not* match, the fix is a failure. Report: "FAIL. [Your rationale]."

EXAMPLE:
- Bug Report: "The Contact us button is blue, it should be red."
- (INTENDED_STATE is 'red')
- Step 1 (Action): `read_html_file()`
- Step 1 (Observation): (HTML content is returned...)
- Step 1 (Thought): "The HTML for 'Contact Us' is `<button class="contact-button">`. The selector is `.contact-button`."
- Step 2 (Action): `verify_element_color(selector_text='.contact-button')`
- Step 2 (Observation): "Found color: #ff0000"
- Step 2 (Judgment): "PASS. The .contact-button background-color is now #ff0000, which is red."
"""

# --- 4. Create the Agent ---

def create_qa_agent():
    """
    Factory function to create and return the QA Agent executor.
    """
    print("Initializing QA Agent (v2)...") # Updated print
    
    # Use the model you've found to be stable
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")
    
    # *** IMPORTANT: Give the agent BOTH tools ***
    tools = [read_html_file, verify_element_color]
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_template),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    print("QA Agent (v2) is ready.")
    return agent_executor

# --- 5. Define the `run` function for the Triage Agent ---
qa_agent_executor = create_qa_agent()

def run(bug_description: str) -> str:
    """
    The main entry point for the QA Agent.
    """
    print(f"QA Agent (v2) received report to verify: '{bug_description}'")
    
    response = qa_agent_executor.invoke({
        "input": bug_description
    })
    
    # Return just the final output string
    return response['output']