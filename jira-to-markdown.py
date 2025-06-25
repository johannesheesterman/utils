import json
import sys

def process_content_list(content_list):
    """Helper to process a list of content nodes."""
    return "".join([process_node(node) for node in content_list])

def process_node(node):
    """Recursively processes a Jira document node and converts it to Markdown."""
    if not node or not isinstance(node, dict):
        return ""

    content = ""
    node_type = node.get("type")
    node_content = node.get("content", [])
    attrs = node.get("attrs", {})
    text = node.get("text", "")

    if node_type == "doc":
        content = process_content_list(node_content)
    elif node_type == "heading":
        level = attrs.get("level", 1)
        text_content = process_content_list(node_content)
        content = f"{'#' * level} {text_content}\n\n"
    elif node_type == "paragraph":
        content = f'{process_content_list(node_content)}\n'
    elif node_type == "text":
        marks = node.get("marks", [])
        for mark in marks:
            mark_type = mark.get("type")
            if mark_type == "strong":
                text = f"**{text}**"
            elif mark_type == "em":
                text = f"*{text}*"
        content = text
    elif node_type == "mediaSingle":
        content = f'{process_content_list(node_content)}\n'
    elif node_type == "media":
        alt_text = attrs.get("alt", "attachment")
        content = f"![{alt_text}]"
    elif node_type == "orderedList":
        for i, item in enumerate(node_content):
            item_text = process_node(item).strip()
            content += f"{i + 1}. {item_text}\n"
    elif node_type == "bulletList":
        for item in node_content:
            item_text = process_node(item).strip()
            content += f"* {item_text}\n"
    elif node_type == "listItem":
        content = process_content_list(node_content)

    return content

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python jira-to-markdown.py <file_path>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        sys.exit(0)

    if not lines:
        sys.exit(0)

    issue_key = lines[0].strip()
    json_content = "".join(lines[1:]).strip()

    if not json_content:
        print(f"{issue_key}\n\n(No description provided)")
        sys.exit(0)

    try:
        data = json.loads(json_content)
        if data is None:
            print(f"{issue_key}\n\n(No description provided)")
        else:
            markdown_content = process_node(data)
            print(f"{issue_key}\n\n{markdown_content.strip()}")
    except json.JSONDecodeError:
        print("".join(lines))