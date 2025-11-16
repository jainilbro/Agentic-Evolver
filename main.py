import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- 1. Load API Key ---
print("Loading environment variables...")
load_dotenv()

# --- 2. Configure the Gemini API ---
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    print("Google API Key configured.")
except Exception as e:
    print(f"Error configuring Google API: {e}")
    print("Please make sure you have a .env file with GOOGLE_API_KEY=YOUR_KEY")
    exit() # Exit if the key is not found

# --- 3. Import Our Agent System ---
# This import works because we have the 'agents/__init__.py' file
from agents import triage_agent
import warnings

# Suppress specific warnings from langchain to keep the output clean
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_core.prompts.chat")

def run_agent_system():
    """
    This is the main function where our agent system will run.
    """
    print("--- AgentOps Self-Healing System ---")
    
    # 1. Get user input:
    print("\nAGENT: Hello! I am the Triage Agent. I can help fix bugs on our website.")
    bug_report = input("AGENT: Please describe the bug: ")
    
    # 2. Start the Triage Agent:
    # This single call will trigger the entire multi-agent workflow
    # (Triage -> Bug-Hunter -> Dev -> QA)
    final_result = triage_agent.run(bug_report)
    
    # 3. Print the full trace and final answer:
    print("\n--- [Triage Agent] FINAL REPORT ---")
    print(final_result['output'])
    print("-----------------------------------")


# --- 4. Start the Program ---
if __name__ == "__main__":
    run_agent_system()