import os
import json

# Define paths
CSS_PATH = os.path.join("world", "style.css")
MEMORY_PATH = os.path.join("memory", "procedural_memory.json")

# 1. The "Buggy" Blue CSS (The Default State)
DEFAULT_CSS = """body {
    font-family: Arial, sans-serif;
    padding: 20px;
}

.contact-button {
    background-color: #007bff; /* This is a shade of blue */
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}"""

def reset_environment():
    print("--- Resetting AgentOps Environment ---")
    
    # Reset CSS
    try:
        with open(CSS_PATH, "w") as f:
            f.write(DEFAULT_CSS)
        print(f"✅ Restored {CSS_PATH} to original 'Blue' state.")
    except Exception as e:
        print(f"❌ Error resetting CSS: {e}")

    # Clear Memory
    try:
        with open(MEMORY_PATH, "w") as f:
            json.dump([], f)
        print(f"✅ Cleared agent memory in {MEMORY_PATH}.")
    except Exception as e:
        print(f"❌ Error clearing memory: {e}")

    print("\nSystem is ready for a fresh demo run!")

if __name__ == "__main__":
    reset_environment()