import os
import json

# Define the file paths our tools will use
CSS_FILE_PATH = os.path.join("world", "style.css")
MEMORY_FILE_PATH = os.path.join("memory", "procedural_memory.json")

def read_css_file() -> str:
    """
    Reads the content of the 'style.css' file.
    Returns the content as a string.
    """
    try:
        with open(CSS_FILE_PATH, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading CSS file: {e}"

def write_css_file(new_content: str) -> str:
    """
    Overwrites the 'style.css' file with new content.
    Takes the new content as a string.
    Returns a success or error message.
    """
    try:
        with open(CSS_FILE_PATH, 'w') as f:
            f.write(new_content)
        return "CSS file updated successfully."
    except Exception as e:
        return f"Error writing to CSS file: {e}"

def update_procedural_memory(bug_description: str, fix_applied: str) -> str:
    """
    Adds a new memory to the 'procedural_memory.json' file.
    Takes a description of the bug and the fix that was applied.
    Returns a success or error message.
    """
    try:
        # Read existing memories
        with open(MEMORY_FILE_PATH, 'r') as f:
            memories = json.load(f)
        
        # Add the new memory
        memories.append({
            "bug": bug_description,
            "fix": fix_applied
        })
        
        # Write the updated list back to the file
        with open(MEMORY_FILE_PATH, 'w') as f:
            json.dump(memories, f, indent=2)
            
        return "Procedural memory updated."
    except Exception as e:
        return f"Error updating memory: {e}"