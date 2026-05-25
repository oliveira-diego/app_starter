# Document Tools

A Python package implementing a variety of document-related tools for converting and processing document formats. These tools are exposed through an MCP server interface for seamless integration with AI assistants.

## Setup

```bash
# Create a virtual env and activate it
uv venv
source .venv/bin/activate

# Install the package in development mode
uv pip install -e .
```

## Running

```bash
# Start the MCP server
uv run main.py
```

## Testing

```bash
# Run all tests
uv run pytest
```

## Available Tools

### `add(a, b)`
Adds two numbers together. Handles both integers and floating-point numbers.

**Parameters:**
- `a` (float): First number to add
- `b` (float): Second number to add

**Returns:** The sum of the two numbers

**Use case:** Simple numerical calculations

### `binary_document_to_markdown(binary_data, file_type)`
Converts binary document data to markdown-formatted text. Supports PDF, DOCX, and other document formats via MarkItDown.

**Parameters:**
- `binary_data` (bytes): The binary content of the document file
- `file_type` (str): File extension/type (e.g., "pdf", "docx")

**Returns:** Markdown-formatted text content

**Use case:** When working with binary document data (e.g., files read by AI assistants)

### `document_path_to_markdown(file_path, file_type)`
Converts a PDF or DOCX file at a given file path to markdown format. This is a convenience wrapper around `binary_document_to_markdown` that handles file I/O.

**Parameters:**
- `file_path` (str): Absolute or relative path to a PDF or DOCX file
- `file_type` (str): File extension/type (e.g., "pdf", "docx"). If empty, infers from file path

**Returns:** Markdown-formatted text content, or an error message if the file cannot be processed

**Supported formats:** PDF, DOCX

**Use cases:**
- Converting local PDF or Word documents to markdown
- Batch processing document files
- Integrating document conversion into workflows

**Examples:**
```python
# Convert a PDF using explicit file type
result = document_path_to_markdown("/path/to/document.pdf", "pdf")

# Convert a DOCX with inferred file type
result = document_path_to_markdown("./report.docx", "")

# Error handling
result = document_path_to_markdown("missing.pdf", "pdf")
# Returns: "Error: File not found - missing.pdf"
```

## Development

### Tool Definitions

Tools are defined as Python functions and registered with the MCP server:

```python
mcp.tool()(my_function)
```

Tool descriptions should:

- Begin with a one-line summary
- Provide detailed explanation of functionality
- Explain when to use (and not use) the tool
- Include usage examples with expected input/output

Use `Field` from pydantic for parameter descriptions:

```python
from pydantic import Field

def my_tool(
    param1: str = Field(description="Detailed description of this parameter"),
    param2: int = Field(description="Explain what this parameter does")
) -> ReturnType:
    """Comprehensive docstring here"""
    # Implementation
```
