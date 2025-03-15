import os
import sys
from bs4 import BeautifulSoup

# Directories to process
templates_dir = "templates"
static_dir = "static/styles"

def clean_html_file(filepath):
    """Remove elements with display:none or hidden from an HTML file."""
    with open(filepath, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Remove elements with inline style "display: none;"
    for element in soup.find_all(style=lambda value: value and "display: none" in value):
        element.decompose()

    # Remove elements with the "hidden" attribute
    for element in soup.find_all(attrs={"hidden": True}):
        element.decompose()

    # Save the cleaned HTML back to the file
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(str(soup))
    print(f"Cleaned {filepath}")

def clean_css_file(filepath, used_classes):
    """Remove unused CSS rules from a CSS file."""
    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()

    cleaned_lines = []
    for line in lines:
        # Keep lines that are not class selectors or are used
        if not line.strip().startswith(".") or any(cls in line for cls in used_classes):
            cleaned_lines.append(line)

    # Save the cleaned CSS back to the file
    with open(filepath, "w", encoding="utf-8") as file:
        file.writelines(cleaned_lines)
    print(f"Cleaned {filepath}")

def get_used_classes(directory):
    """Extract all class names used in HTML files."""
    used_classes = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".htm") or file.endswith(".html"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f, "html.parser")
                    for element in soup.find_all(class_=True):
                        used_classes.update(element["class"])
    return used_classes

def main():
    if len(sys.argv) == 2:
        # Process a single file
        filepath = sys.argv[1]
        if filepath.endswith(".htm") or filepath.endswith(".html"):
            clean_html_file(filepath)
        elif filepath.endswith(".css"):
            # Get all used classes from the templates directory
            used_classes = get_used_classes(templates_dir)
            clean_css_file(filepath, used_classes)
        else:
            print("Unsupported file type. Please provide an HTML or CSS file.")
    else:
        # Process all files in the directories
        # Step 1: Clean HTML files
        for root, _, files in os.walk(templates_dir):
            for file in files:
                if file.endswith(".htm") or file.endswith(".html"):
                    clean_html_file(os.path.join(root, file))

        # Step 2: Get all used classes from HTML files
        used_classes = get_used_classes(templates_dir)

        # Step 3: Clean CSS files
        for root, _, files in os.walk(static_dir):
            for file in files:
                if file.endswith(".css"):
                    clean_css_file(os.path.join(root, file), used_classes)

if __name__ == "__main__":
    main()

def display_none(line, key):
    # Handle escaped double quotes explicitly
    escaped_key = key.replace('\\"', '')  # Properly handle escaped quotes

    # Check for matches in the line
    if key in line or escaped_key in line:
        print(f"Match found for key: {key} in line: {line.strip()}")

        # Avoid adding duplicate attributes
        if 'style="display: none;" hidden' not in line:
            # Handle elements with id matching the key (e.g., <div id="Segments">)
            if f'id="{key}"' in line or f'id="{escaped_key}"' in line:
                print(f"Modifying line with id: {line.strip()}")
                line = line.replace(f'id="{key}"', f'id="{key}" style="display: none;" hidden')
                line = line.replace(f'id="{escaped_key}"', f'id="{escaped_key}" style="display: none;" hidden')
            # Handle tab button content (e.g., <button>Segments</button>)
            elif f">{key}" in line or f">{escaped_key}" in line:
                print(f"Modifying line with content: {line.strip()}")
                line = line.replace(f">{key}", f" style=\"display: none;\" hidden>{key}")
                line = line.replace(f">{escaped_key}", f" style=\"display: none;\" hidden>{escaped_key}")

        print(f"Modified line: {line.strip()}")

    return line