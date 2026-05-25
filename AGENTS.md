# AI Agent Guidelines for MCP Document Tools

This project implements a Model Context Protocol (MCP) server that exposes Python functions as tools for AI assistants to call. This document helps AI agents understand the codebase structure and conventions for effective contribution.

## Quick Start

### Essential Commands
```bash
# Setup and dependencies
uv venv                    # Create virtual environment
source .venv/bin/activate  # Activate venv (Windows: .venv\Scripts\activate)
uv pip install -e .        # Install package in dev mode

# Running and testing
uv run main.py            # Start the MCP server
uv run pytest             # Run all tests
```

### Project Structure
- **`main.py`**: Entry point that initializes the FastMCP server and registers tools
- **`tools/`**: Module containing tool implementations
  - `math.py`: Mathematical tools (e.g., `add`)
  - `document.py`: Document conversion tools (e.g., `binary_document_to_markdown`)
- **`tests/`**: Test suite using pytest
  - `test_document.py`: Tests for document conversion tools
  - `fixtures/`: Sample files for testing (DOCX, PDF, etc.)

## How Tools Work

### MCP Server Pattern
The project uses FastMCP (a lightweight MCP server framework) to expose Python functions as tools:

```python
from mcp.server.fastmcp import FastMCP
from tools.math import add

mcp = FastMCP("docs")  # Create server with name
mcp.tool()(add)         # Register function as a tool
```

When a tool is registered, the MCP server automatically:
1. Exposes it via the protocol for AI assistants to call
2. Uses the function's docstring and type hints as tool description and parameters
3. Validates inputs using Pydantic

### Tool Definition Convention

All tools must follow this pattern (see [README.md](README.md#development) for reference):

```python
from pydantic import Field

def my_tool(
    param1: str = Field(description="What this parameter does"),
    param2: int = Field(description="What this parameter does"),
) -> str:
    """One-line summary of what the tool does.
    
    Detailed explanation of functionality and behavior.
    Can span multiple lines.
    
    When to use:
    - Use case 1
    - Use case 2
    
    When NOT to use:
    - Avoid when...
    
    Examples:
    >>> my_tool("input", 42)
    "output"
    """
    # Implementation
    return result
```

**Key points:**
- Always use `Field(description=...)` for parameters (not inline comments)
- Include a comprehensive docstring with: summary, details, "When to use" section, examples
- Use clear type hints for all parameters and return values
- Return simple types that serialize well (str, int, bool, list, dict)

### Detailed Tool Definition Guide

#### 1. Parameter Definitions with `Field`
Every parameter **must** use `Field(description=...)`. The MCP framework uses these descriptions to:
- Generate the OpenAI/Claude API schema that AI assistants see
- Validate inputs using Pydantic
- Provide parameter help to end users

```python
# ✓ CORRECT
def process_file(
    file_path: str = Field(description="Absolute or relative path to the file to process"),
    max_lines: int = Field(description="Maximum number of lines to read; if 0, read entire file"),
) -> str:
    ...

# ✗ WRONG - Missing description details
def process_file(
    file_path: str = Field(description="file path"),  # Too vague
    max_lines: int = Field(description="max lines"),   # Ambiguous
) -> str:
    ...
```

**Field description best practices:**
- Be specific about input format and constraints (e.g., "Path to DOCX file", "Number between 1-100")
- Mention default behavior if parameter is optional (e.g., "If 0, process entire file")
- Include file type or expected format for string inputs

#### 2. Type Hints and Serialization
The MCP server transmits tool responses as JSON. **Return only serializable types**:

| ✓ Serializable | ✗ Non-serializable |
|---|---|
| `str`, `int`, `float`, `bool` | Custom classes |
| `list`, `dict` | `BytesIO`, file objects |
| `list[dict]`, `dict[str, int]` | Dataclass instances |
| `None` (void return) | NumPy arrays, Pandas DataFrames |

If your tool produces complex output, convert to `dict` or `list[dict]`:
```python
# ✗ WRONG
def analyze_file(path: str) -> FileAnalysisResult:  # Custom class won't serialize
    return FileAnalysisResult(size=1024, lines=50)

# ✓ CORRECT
def analyze_file(path: str) -> dict:
    return {
        "size": 1024,
        "lines": 50,
        "encoding": "utf-8"
    }
```

#### 3. Comprehensive Docstrings
The docstring is critical—AI assistants use it to understand *when* and *how* to call your tool. Structure it as:

```python
def convert_markdown_to_html(
    markdown_content: str = Field(description="The markdown text to convert"),
    include_toc: bool = Field(description="Whether to include a table of contents"),
) -> str:
    """Convert markdown text to HTML.
    
    Transforms markdown-formatted text into valid HTML using CommonMark spec.
    Supports headings, lists, code blocks, links, images, and emphasis.
    
    When to use:
    - Converting markdown documentation to web-displayable HTML
    - Generating HTML from user-provided markdown input
    - Building static site generators
    
    When NOT to use:
    - For rendering markdown in markdown viewers (use markdown renderers instead)
    - If you need to preserve markdown source (convert back to markdown)
    - For performance-critical markdown rendering (use compiled markdown engines)
    
    Examples:
    >>> convert_markdown_to_html("# Header\\n\\nParagraph with **bold**")
    '<h1>Header</h1><p>Paragraph with <strong>bold</strong></p>'
    >>> convert_markdown_to_html("- Item 1\\n- Item 2", include_toc=True)
    '<nav>...</nav><ul><li>Item 1</li><li>Item 2</li></ul>'
    """
    # Implementation
```

**Docstring sections (in order):**
1. **One-line summary**: What the tool does (not how)
2. **Detailed explanation**: Behavior, edge cases, transformation details
3. **When to use**: Specific scenarios where the tool is appropriate (2-3 bullet points)
4. **When NOT to use**: Anti-patterns and situations to avoid (2-3 bullet points)
5. **Examples**: 2-3 `>>> ` examples showing realistic input/output

The "When to use / When NOT to use" sections are crucial for AI assistants to make good decisions about tool selection.

## Adding New Tools

### Step 1: Create the tool function
1. Create a new file in `tools/` (e.g., `tools/pdf.py`)
2. Implement the function with proper docstring and Field descriptions
3. Keep the function focused on one task

### Step 2: Register in main.py
```python
from tools.pdf import extract_pdf_text

mcp.tool()(extract_pdf_text)
```

### Step 3: Write tests
1. Create tests in `tests/test_<feature>.py`
2. Use the `FIXTURES_DIR` pattern to locate test files
3. Follow existing test patterns (see `test_document.py`)

### Step 4: Update README.md and dependencies
- Add tool description to README
- Update `pyproject.toml` dependencies if needed

## Testing

### Test Conventions
- Place test files in `tests/` with names like `test_<feature>.py`
- Use pytest framework
- Store test fixtures (sample files) in `tests/fixtures/`
- Use the pattern from `test_document.py` to locate fixtures:
  ```python
  FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
  FIXTURE_PATH = os.path.join(FIXTURES_DIR, "filename.ext")
  ```

### Running Tests
```bash
uv run pytest              # Run all tests
uv run pytest tests/test_document.py  # Run specific test file
uv run pytest -v          # Verbose output
```

## Dependencies

Key dependencies (see `pyproject.toml`):
- **markitdown**: Document format conversion (DOCX, PDF, HTML, etc.)
- **mcp**: Model Context Protocol server framework
- **pydantic**: Data validation using type hints
- **pytest**: Testing framework
- **uv**: Fast Python package manager

## Common Patterns

### Document Processing
The `binary_document_to_markdown` tool uses MarkItDown for format conversion:
```python
from markitdown import MarkItDown, StreamInfo
from io import BytesIO

def convert_doc(binary_data: bytes, file_type: str) -> str:
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content
```

**Key lessons for binary tool design:**
- Accept `bytes` parameter for binary document data (AI assistants will read files as binary)
- Use `BytesIO` to simulate file objects for processing libraries
- Return `str` (or `dict` with string content), never return file objects or BytesIO

### Error Handling in Tools
Tools should handle expected errors gracefully and return informative error messages:

```python
def safe_tool(data: str) -> str:
    """Process data safely.
    
    When to use:
    - When processing user-provided data that may be invalid
    
    When NOT to use:
    - For performance-critical operations (error handling adds overhead)
    """
    try:
        # Process
        return result
    except ValueError as e:
        return f"Error: Invalid input - {str(e)}"
    except FileNotFoundError as e:
        return f"Error: File not found - {str(e)}"
```

**Best practices for error handling:**
- Return error messages as strings (not exceptions)—this allows AI assistants to see the error
- Include error type/context in the message (e.g., "File not found:", "Invalid format:")
- Don't raise exceptions; let the caller handle the error message
- Test both success and failure paths in your tests

### Advanced: Optional Parameters and Complex Returns
For tools with optional behavior, use Optional types and document defaults:

```python
from typing import Optional

def analyze_document(
    content: str = Field(description="Document text to analyze"),
    language: str = Field(description="Language code (e.g., 'en', 'es', 'fr'); defaults to 'en'"),
    include_sentiment: bool = Field(description="Whether to include sentiment analysis; default False"),
) -> dict:
    """Analyze document content for structure and meaning.
    
    Returns a structured analysis including word count, key themes, and optional sentiment.
    """
    result = {
        "word_count": len(content.split()),
        "language": language,
    }
    if include_sentiment:
        result["sentiment"] = _compute_sentiment(content)
    return result
```

**Key points:**
- Use clear parameter names to indicate optionality
- Document default behavior in Field descriptions
- Return `dict` for complex results; structure with consistent keys
- Always include the most basic fields (don't make everything optional)

## Important Notes

### Pitfalls to Avoid

1. **Non-serializable return types**: Don't return custom objects; use str, dict, list, or primitives
   - ✗ Returns: Custom class, dataclass, object instance
   - ✓ Returns: `str`, `dict`, `list[dict]`, `bool`, `int`

2. **Missing Field descriptions**: Always use `Field(description=...)` for parameters
   - ✗ `param: str` (no description)
   - ✓ `param: str = Field(description="Specific description of what this does")`
   - The description is used to generate the AI assistant API schema

3. **Incomplete docstrings**: Include all required sections
   - Must have: one-line summary, detailed explanation, "When to use", "When NOT to use", examples
   - Missing docstring sections make it hard for AI assistants to use the tool correctly

4. **Binary vs Text**: Handle file data correctly
   - ✗ Opening DOCX/PDF files as text mode (`open(path, 'r')`)
   - ✓ Reading binary files as bytes (`open(path, 'rb')` or `BytesIO` for streaming)

5. **Forgetting to register**: New tools must be registered in `main.py` with `mcp.tool()`
   - Without registration, the tool won't be exposed to AI assistants

6. **Vague parameter descriptions**: Be specific about what each parameter does
   - ✗ `Field(description="text")` or `Field(description="data")`
   - ✓ `Field(description="Markdown-formatted text to convert to HTML")`
   - Specific descriptions help AI assistants provide the right inputs

7. **Ignoring type hints**: Always annotate parameters and return types
   - Type hints are essential for Pydantic validation and MCP schema generation
   - Missing hints = tools that AI assistants can't reliably use

### How MCP Tool Integration Works

When you register a tool with `mcp.tool()`, the FastMCP framework:

1. **Inspects the function** to extract:
   - Function name → tool name
   - Type hints → parameter types in the API schema
   - `Field(description=...)` values → parameter descriptions in the API schema
   - Function docstring → tool description and documentation

2. **Generates OpenAI/Claude API schema** using Pydantic, which:
   - Validates all function calls from AI assistants
   - Ensures correct parameter types
   - Rejects calls with missing required parameters
   - Provides type coercion (e.g., string to int)

3. **Exposes via MCP protocol** so AI assistants can:
   - See the tool in their available tools list
   - Understand tool purpose from docstring
   - Understand parameters from Field descriptions
   - Call the tool with confidence that inputs are validated

This means **every detail of your tool definition matters**—it directly affects how AI assistants understand and use your tool.

### Notes on MarkItDown
- Supports multiple formats: DOCX, PDF, HTML, XLSX, PPTX, and more
- Returns `MarkdownifyResult` with `.text_content` property
- Handles streams via `BytesIO` and `StreamInfo`

## Typical Development Workflow

1. **Create tool**: Implement in `tools/<feature>.py` with full docstring
2. **Register**: Add to `main.py` with `mcp.tool()()`
3. **Test**: Create `tests/test_<feature>.py` with comprehensive tests
4. **Run**: `uv run pytest` to verify tests pass
5. **Run server**: `uv run main.py` to test tool availability
6. **Document**: Update [README.md](README.md) with tool description

## Tool Definition Validation Checklist

Before submitting a new tool, verify:

- [ ] **Function signature**: All parameters have `Field(description=...)`
- [ ] **Type hints**: Parameters and return value have clear type annotations
- [ ] **Return type**: Serializable (str, int, dict, list—not custom objects)
- [ ] **Docstring sections**: One-line summary, details, "When to use", "When NOT to use", examples
- [ ] **Examples**: 2-3 realistic `>>>` examples with expected output
- [ ] **Field descriptions**: Specific and actionable (not vague like "data" or "text")
- [ ] **Registration**: Function is registered in `main.py` with `mcp.tool()()`
- [ ] **Tests**: Unit tests exist in `tests/test_<feature>.py`
- [ ] **Error handling**: Expected errors are caught and returned as error messages
- [ ] **Binary files**: Correctly uses `rb` mode or `BytesIO` for document processing

## References

See [README.md](README.md) for setup and running instructions, tool definition templates, and best practices for parameter descriptions and docstrings.
