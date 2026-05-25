import os
import pytest
from tools.document import document_path_to_markdown


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
PDF_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.pdf")
DOCX_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.docx")


class TestDocumentPathToMarkdown:
    """Test suite for document_path_to_markdown function."""
    
    def test_fixtures_exist(self):
        """Verify test fixtures are available."""
        assert os.path.exists(PDF_FIXTURE), f"PDF fixture not found: {PDF_FIXTURE}"
        assert os.path.exists(DOCX_FIXTURE), f"DOCX fixture not found: {DOCX_FIXTURE}"
    
    def test_convert_pdf_with_explicit_type(self):
        """Test converting a PDF file with explicit file type."""
        result = document_path_to_markdown(PDF_FIXTURE, "pdf")
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"
        assert "Error" not in result[:10], "Should not return an error message"
    
    def test_convert_docx_with_explicit_type(self):
        """Test converting a DOCX file with explicit file type."""
        result = document_path_to_markdown(DOCX_FIXTURE, "docx")
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"
        assert "Error" not in result[:10], "Should not return an error message"
    
    def test_convert_pdf_with_inferred_type(self):
        """Test converting a PDF file with inferred file type."""
        result = document_path_to_markdown(PDF_FIXTURE, "")
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"
        assert "Error" not in result[:10], "Should not return an error message"
    
    def test_convert_docx_with_inferred_type(self):
        """Test converting a DOCX file with inferred file type."""
        result = document_path_to_markdown(DOCX_FIXTURE, "")
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"
        assert "Error" not in result[:10], "Should not return an error message"
    
    def test_file_not_found(self):
        """Test handling of non-existent file path."""
        result = document_path_to_markdown("/nonexistent/path/file.pdf", "pdf")
        assert isinstance(result, str), "Result should be a string"
        assert "Error: File not found" in result, "Should return file not found error"
    
    def test_unsupported_file_type(self):
        """Test handling of unsupported file type."""
        result = document_path_to_markdown(PDF_FIXTURE, "txt")
        assert isinstance(result, str), "Result should be a string"
        assert "Error: Unsupported file type" in result, "Should return unsupported type error"
        assert "txt" in result, "Error message should mention the unsupported type"
    
    def test_unsupported_file_type_with_inferred_extension(self):
        """Test handling of unsupported file type when inferred from extension."""
        # Create a temporary file with unsupported extension
        temp_file = os.path.join(FIXTURES_DIR, "test.txt")
        try:
            with open(temp_file, "w") as f:
                f.write("test content")
            result = document_path_to_markdown(temp_file, "")
            assert "Error: Unsupported file type" in result, "Should return unsupported type error"
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_directory_path(self):
        """Test handling of directory path instead of file path."""
        result = document_path_to_markdown(FIXTURES_DIR, "pdf")
        assert isinstance(result, str), "Result should be a string"
        assert "Error: Path is not a file" in result, "Should return path is not a file error"
    
    def test_relative_path(self):
        """Test conversion with relative path."""
        # Change to the project directory
        original_cwd = os.getcwd()
        try:
            os.chdir(os.path.dirname(os.path.dirname(__file__)))
            relative_path = os.path.relpath(PDF_FIXTURE)
            result = document_path_to_markdown(relative_path, "pdf")
            assert isinstance(result, str), "Result should be a string"
            assert len(result) > 0, "Result should not be empty"
            assert "Error" not in result[:10], "Should not return an error message"
        finally:
            os.chdir(original_cwd)
    
    def test_result_is_markdown_string(self):
        """Test that result is markdown-formatted content."""
        result = document_path_to_markdown(PDF_FIXTURE, "pdf")
        assert isinstance(result, str), "Result should be a string"
        # Markdown content typically contains newlines
        assert "\n" in result or len(result) > 50, "Result should be substantial markdown content"
