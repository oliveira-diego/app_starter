from markitdown import MarkItDown, StreamInfo
from io import BytesIO
from pathlib import Path
from pydantic import Field


def binary_document_to_markdown(binary_data: bytes, file_type: str) -> str:
    """Converts binary document data to markdown-formatted text."""
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content


def document_path_to_markdown(
    file_path: str = Field(description="Absolute or relative path to a PDF or DOCX file to convert"),
    file_type: str = Field(description="File extension/type (e.g., 'pdf', 'docx'). If empty, infers from file path"),
) -> str:
    """Convert a PDF or DOCX file to markdown format.
    
    Reads a document file from the specified path and converts its contents
    to markdown-formatted text. Supports PDF and DOCX formats. The tool handles
    text extraction, formatting preservation, and structural elements like
    headings, lists, and tables.
    
    When to use:
    - Converting local PDF or Word documents to markdown
    - Batch processing multiple document files
    - Integrating document conversion into automated workflows
    - Preparing documents for use with markdown-based tools and systems
    
    When NOT to use:
    - For very large files (>100MB) where performance is critical
    - For binary streaming data (use binary_document_to_markdown instead)
    - If documents are already in markdown format
    - For image-only PDFs without text (will return minimal content)
    
    Examples:
    >>> document_path_to_markdown("/path/to/document.pdf")
    "# Document Title\\n\\nContent here...\\n"
    >>> document_path_to_markdown("./report.docx", "docx")
    "# Report\\n\\n## Section 1\\n..."
    >>> document_path_to_markdown("invalid.txt")
    "Error: Unsupported file type 'txt'. Supported types: pdf, docx"
    """
    try:
        # Resolve the file path
        file_path_obj = Path(file_path)
        
        # Check if file exists
        if not file_path_obj.exists():
            return f"Error: File not found - {file_path}"
        
        # Check if it's a file (not a directory)
        if not file_path_obj.is_file():
            return f"Error: Path is not a file - {file_path}"
        
        # Determine file type
        if not file_type or file_type.strip() == "":
            # Infer from file extension
            file_type = file_path_obj.suffix.lstrip(".").lower()
        else:
            file_type = file_type.strip().lower()
        
        # Validate file type
        supported_types = {"pdf", "docx"}
        if file_type not in supported_types:
            return f"Error: Unsupported file type '{file_type}'. Supported types: {', '.join(sorted(supported_types))}"
        
        # Read the file in binary mode
        with open(file_path_obj, "rb") as f:
            binary_data = f.read()
        
        # Convert using existing function
        markdown_content = binary_document_to_markdown(binary_data, file_type)
        return markdown_content
        
    except PermissionError:
        return f"Error: Permission denied - cannot read file {file_path}"
    except OSError as e:
        return f"Error: Failed to read file - {str(e)}"
    except Exception as e:
        return f"Error: Conversion failed - {str(e)}"
