import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# --- 1. Import This Agent's Specific Tools ---
# NOW IT HAS TWO TOOLS: ONE FOR HTML, ONE FOR CSS
from tools.web_inspector import get_element_color, get_html_content

# --- 2. Wrap the Tools for the Agent ---
@tool
def read_html_file() -> str:
    """
    Reads and returns the entire content of the 'index.html' file.
    Use this tool FIRST to inspect the HTML and find the
    correct CSS selector for a given element.
    """
    print(f"\n--- [Bug-Hunter Tool] Reading index.html ---")
    return get_html_content()

@tool
def inspect_element_color(selector_text: str) -> str:
    """
    Finds a specific CSS rule by its selector (e.q., '.contact-button')
    and returns its 'background-color' property.
    Use this tool SECOND, *after* you have found the selector.
    """
    print(f"\n--- [Bug-Hunter Tool] Inspecting CSS for: {selector_text} ---")
    return get_element_color(selector_text)


# --- 3. Define the Agent's "Constitution" (System Prompt) ---
# This prompt is now much smarter and teaches a 2-step logic.
prompt_template = """
You are a "Bug-Hunter Agent." Your one and only job is to validate if a user's bug report about a color is *accurate*.

You MUST use a 2-step process to find the bug:
1.  **FIND SELECTOR:** The user's report is in plain English (e.g., "Contact us button").
    You MUST call the `read_html_file` tool first to get the site's HTML.
    Then, you must analyze this HTML to find the *exact* CSS selector for the element the user is describing.
2.  **INSPECT COLOR:** After you have the selector, you MUST call the `inspect_element_color` tool with that selector.

Finally, compare the user's claim with the tool's finding to make your judgment.

-   If the user's claim *matches* the tool's finding (e.g., user says "blue" and tool finds "#007bff"), the bug is real.
    Respond with: "VALIDATED. The user's report is accurate. The element [selector] is [color]."
-   If the user's claim does *not match* the tool's finding (e.g., user says "red" but tool finds "#007bff"), the bug is not real.
    Respond with: "NOT VALID. The user's report is inaccurate. The user claimed [color 1], but the tool found [color 2]."

EXAMPLE:
- Bug Report: "The Contact us button is blue, it should be red."
- Step 1 (Action): `read_html_file()`
- Step 1 (Observation): (HTML content is returned...)
- Step 1 (Thought): "The HTML for 'Contact Us' is `<button class="contact-button">`. The selector is `.contact-button`."
- Step 2 (Action): `inspect_element_color(selector_text='.contact-button')`
- Step 2 (Observation): "Found color: #007bff"
- Step 2 (Judgment): "VALIDATED. The user's report is accurate. The element .contact-button is #007bff (blue)."
"""

# --- 4. Create the Agent ---

def create_bug_hunter_agent():
    """
    Factory function to create and return the Bug-Hunter Agent executor.
    """
    print("Initializing Bug-Hunter Agent (v2)...") # Updated print
    
    # Use the model you've found to be stable
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")
    
    # *** IMPORTANT: Give the agent BOTH tools ***
    tools = [read_html_file, inspect_element_color]
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_template),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    print("Bug-Hunter Agent (v2) is ready.")
    return agent_executor

# --- 5. Define the `run` function for the Triage Agent ---
bug_hunter_executor = create_bug_hunter_agent()

def run(bug_description: str) -> str:
    """
    The main entry point for the Bug-Hunter Agent.
    """
    print(f"Bug-Hunter Agent (v2) received report: '{bug_description}'")
    
    response = bug_hunter_executor.invoke({
        "input": bug_description
    })
    
    # Return just the final output string
    return response['output']