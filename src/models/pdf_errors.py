"""Custom exception classes for PDF-related errors."""

class PDFError(Exception):
    """Base class for PDF-related errors."""
    pass

class PDFDocumentError(PDFError):
    """Error related to PDF document operations.
    
    Examples:
        - Document not loaded
        - Cannot open document
        - Cannot save document
    """
    pass

class PDFPageError(PDFError):
    """Error related to PDF page operations.
    
    Examples:
        - Page index out of range
        - Cannot delete page
        - Cannot move page
    """
    pass

class PDFImageError(PDFError):
    """Error related to PDF image operations.
    
    Examples:
        - Image extraction failed
        - Invalid image format
        - Cannot insert image
    """
    pass

class PDFTextError(PDFError):
    """Error related to PDF text operations.
    
    Examples:
        - Text extraction failed
        - Invalid text format
        - Cannot insert text
    """
    pass