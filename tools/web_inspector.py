import cssutils
import os
from bs4 import BeautifulSoup

HTML_FILE_PATH = os.path.join("world", "index.html")
CSS_FILE_PATH = os.path.join("world", "style.css")

def get_html_content() -> str:
    """
    Reads and returns the entire content of the 'index.html' file.
    The agent can use this to find CSS selectors.
    """
    try:
        with open(HTML_FILE_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading HTML file: {e}"
    
def get_element_color(selector_text: str) -> str:
    """
    Finds a specific CSS rule by its selector (e.g., '.contact-button')
    and returns its 'background-color' property.
    
    Args:
        selector_text: The CSS selector to find (e.g., '.contact-button').
    
    Returns:
        The color value (e.g., '#007bff') or an error message.
    """
    try:
        # Use cssutils to parse the CSS file
        parser = cssutils.CSSParser()
        stylesheet = parser.parseFile(CSS_FILE_PATH)
        
        # Loop through the rules in the stylesheet
        for rule in stylesheet:
            if rule.type == rule.STYLE_RULE:
                # Check if this rule is the one we're looking for
                if rule.selectorText == selector_text:
                    # Find the background-color property
                    color = rule.style.getPropertyValue('background-color')
                    if color:
                        return f"Found color: {color}"
                    else:
                        return f"Selector '{selector_text}' found, but 'background-color' property is not set."
                        
        return f"Error: CSS selector '{selector_text}' not found in style.css."
        
    except Exception as e:
        return f"Error inspecting CSS: {e}"