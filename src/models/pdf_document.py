import fitz  # PyMuPDF
from .document_cache import DocumentCache
from typing import List, Tuple, Union, Optional, Callable
from functools import wraps
from .pdf_errors import (
    PDFError,
    PDFDocumentError,
    PDFPageError
)

def require_document(f: Callable):
    """Decorator that checks if a document is loaded before executing a method.
    
    Args:
        f: The method to wrap
    """
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.doc:
            raise PDFDocumentError(f"Cannot {f.__name__}: No document loaded")
        return f(self, *args, **kwargs)
    return wrapper

class PDFDocument:
    """
    Represents a PDF document, providing an interface to interact with it
    using PyMuPDF.

    Args:
        filepath (str, optional): The path to the PDF file. If provided, the
            document is loaded immediately. Defaults to None.
    """
    def __init__(self, filepath: str = None):
        self.filepath = filepath
        self.doc: fitz.Document = None
        self._cache = DocumentCache()
        if filepath:
            self.load(filepath)

    def load(self, filepath: str) -> None:
        """
        Loads a PDF document from the specified file path.

        Args:
            filepath (str): The path to the PDF file.

        Raises:
            PDFDocumentError: If the file cannot be opened.
        """
        try:
            self.doc = fitz.open(filepath)
            self._cache.clear()  # Clear cache on new document load
            self.filepath = filepath
        except Exception as e:
            raise PDFDocumentError(f"Failed to open PDF document: {str(e)}")

    def save(self, filepath: str, garbage: int = 4, deflate: bool = True, clean: bool = False) -> None:
        """
        Saves the PDF document to the specified file path.

        Args:
            filepath (str): The path to save the PDF file.
            garbage (int):  Garbage collection level (0-4).  Higher numbers
                usually result in smaller file sizes but take longer.
                0: no garbage collection,
                1: compact xref table,
                2: compact xref and remove unreferenced objects,
                3: merge duplicate objects,
                4: merge duplicate objects and compress streams.
            deflate (bool): Whether to deflate uncompressed streams.
            clean (bool):  Whether to sanitize content streams.

        Raises:
            PDFDocumentError: If the document is not loaded.
            PDFError: If the save operation fails.
        """
        if not self.doc:
            raise PDFDocumentError("Cannot save: No document loaded.")
        
        try:
            # If saving to the original file, we must use incremental save
            if filepath == self.filepath:
                self.doc.save(
                    filepath,
                    incremental=True,
                    encryption=self.doc.is_encrypted
                )
            else:
                # When saving to a new file, we can use the optimization parameters
                self.doc.save(
                    filepath,
                    garbage=garbage,
                    deflate=deflate,
                    clean=clean,
                    incremental=False,
                    encryption=self.doc.is_encrypted
                )
        except Exception as e:
            raise PDFError(f"Failed to save PDF: {str(e)}")

    def close(self) -> None:
        """
        Closes the PDF document and releases resources.
        """
        if self.doc:
            self.doc.close()
            self.doc = None
            self._cache.clear()  # Clear cache when closing
            self.filepath = None
            
    def __enter__(self):
        """
        Context manager entry point.
        
        Returns:
            PDFDocument: The PDFDocument instance.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point. Ensures the document is properly closed.
        
        Args:
            exc_type: The type of the exception that occurred, if any
            exc_val: The instance of the exception that occurred, if any
            exc_tb: The traceback of the exception that occurred, if any
        """
        self.close()

    @property
    def page_count(self) -> int:
        """
        The total number of pages in the document.

        Returns:
            int: The number of pages.
        """
        return self.doc.page_count if self.doc else 0

    @property
    def metadata(self) -> dict:
        """
        The document's metadata.

        Returns:
             dict: A dictionary containing the document's metadata.  Returns
                 an empty dictionary if no document is loaded.
        """
        return self.doc.metadata if self.doc else {}

    @property
    def toc(self) -> List[List]:
        """
        The document's table of contents (TOC).

        Returns:
            list: The table of contents as a list of lists.  Each inner list
            represents a TOC entry. Returns an empty list if no document is loaded.
        """
        return self.doc.get_toc() if self.doc else []
    
    @require_document
    def delete_page(self, page_number: int) -> None:
        """
        Deletes a page from the document.

        Args:
            page_number (int): The zero-based index of the page to delete.

        Raises:
            PDFPageError: If the page number is out of range.
            PDFDocumentError: If no document is loaded.
        """
        if 0 <= page_number < self.doc.page_count:
            self.doc.delete_page(page_number)
            self._cache.remove_page(page_number)  # Remove from cache
        else:
            raise PDFPageError("Page number out of range.")

    @require_document
    def delete_pages(self, from_page: int, to_page: int) -> None:
        """
        Deletes a range of pages from the document.

        Args:
            from_page (int): The zero-based index of the first page to delete.
            to_page (int): The zero-based index of the last page to delete.

        Raises:
            PDFPageError: If the page numbers are out of range.
            PDFDocumentError: If no document is loaded.
        """
        if 0 <= from_page <= to_page < self.doc.page_count:
            self.doc.delete_pages(from_page=from_page, to_page=to_page)
            for page_num in range(from_page, to_page + 1):
                self._cache.remove_page(page_num)  # Remove from cache
        else:
            raise PDFPageError("Page numbers out of range.")
    
    @require_document
    def move_page(self, from_page: int, to_page: int) -> None:
        """
        Moves a page within the document.

        Args:
            from_page (int): The zero-based index of the page to move.
            to_page (int): The zero-based index where the page will be inserted.
        
        Raises:
            PDFPageError: If the page numbers are out of range.
            PDFDocumentError: If no document is loaded.
        """
        if 0 <= from_page < self.doc.page_count and 0 <= to_page < self.doc.page_count:
            self.doc.move_page(from_page, to_page)
            # Clear affected pages from cache
            self._cache.remove_page(from_page)
            self._cache.remove_page(to_page)
        else:
            raise PDFPageError("Page number out of range.")
    
    @require_document
    def copy_page(self, page_number: int, to_page: int = -1) -> None:
        """
        Copy a page within the document.

        Args:
            page_number (int): The zero-based index of the page to copy.
            to_page (int): The zero-based index where the page should be copied to.
                If -1, copy to end of the document.

        Raises:
            PDFPageError: If the page numbers are out of range.
            PDFDocumentError: If no document is loaded.
        """
        if 0 <= page_number < self.doc.page_count:
            self.doc.copy_page(page_number, to_page)
            # Clear cache as page numbers may have shifted
            self._cache.clear()
        else:
            raise PDFPageError("Page number out of range.")

    @require_document
    def select(self, page_list: List[int]) -> None:
        """
        Selects a subset of pages to keep in the document, removing all others.

        Args:
            page_list (list[int]): A list of zero-based page numbers to keep.
                The order determines the new page order. Pages can be repeated.

        Raises:
            PDFPageError: If any page number in the list is out of range.
            PDFDocumentError: If no document is loaded.
        """
        if all(0 <= p < self.doc.page_count for p in page_list):
            self.doc.select(page_list)
            self._cache.clear()  # Clear cache as page order changed
        else:
            raise PDFPageError("Invalid page number(s) in selection list.")

    @require_document
    def new_page(self, pno: int = -1, width: float = -1, height: float = -1) -> fitz.Page:
        """
        Creates a new page in the PDF.

        Args:
            pno: Where to insert: -1 means at the end (default).
                Supports insertion in front of 0.
            width: page width.
            height: page height.

        Returns:
            fitz.Page: The new page object, or None if failed.

        Raises:
            PDFDocumentError: If no document is loaded.
        """
        page = self.doc.new_page(pno=pno, width=width, height=height)
        if page and pno >= 0:
            self._cache.remove_page(pno)  # Clear cache for affected position
        return page

    @require_document
    def get_page_image(self, page_number: int, zoom: float = 1.0) -> Optional[fitz.Pixmap]:
        """
        Gets a pixmap representation of a page for display.

        Args:
            page_number (int): The zero-based index of the page.
            zoom (float): The zoom factor. Defaults to 1.0.

        Returns:
            Optional[fitz.Pixmap]: A Pixmap object representing the page image,
                or None if the page number is invalid.

        Raises:
            PDFDocumentError: If no document is loaded.
        """
        if 0 <= page_number < self.doc.page_count:
            page = self.doc.load_page(page_number)
            
            # Check cache first
            cached_image = self._cache.get_page_image(page, zoom)
            if cached_image:
                return cached_image
            
            # Generate and cache if not found
            matrix = fitz.Matrix(zoom, zoom)
            pixmap = page.get_pixmap(matrix=matrix)
            self._cache.add_page_image(page, pixmap, zoom)
            return pixmap
        return None
    
    @require_document
    def get_page_text(self, page_number: int, text_type: str = "text") -> Optional[str]:
        """
        Gets text from page.

        Args:
            page_number: Number of the page.
            text_type: Type of the text. One of: "text", "blocks", "words", 
                "html", "dict", "json", "rawdict", "rawjson", "xhtml", "xml"

        Returns:
            Optional[str]: Text of the page as string, or None if the page 
                number is invalid.

        Raises:
            PDFDocumentError: If no document is loaded.
        """
        if 0 <= page_number < self.doc.page_count:
            page = self.doc.load_page(page_number)
            return page.get_text(text_type)
        return None
    
    @require_document
    def search_page_for(self, page_number: int, text: str, quads: bool = False) -> List[Union[fitz.Rect, fitz.Quad]]:
        """
        Searches text on a page.

        Args:
            page_number: Number of the page.
            text: Text for searching.
            quads: return quads instead of rectangles.

        Returns:
            List[Union[fitz.Rect, fitz.Quad]]: If quads is False, a list of 
                fitz.Rect objects each surrounding a found occurrence. If quads 
                is True, a list of fitz.Quad.

        Raises:
            PDFDocumentError: If no document is loaded.
        """
        if 0 <= page_number < self.doc.page_count:
            page = self.doc.load_page(page_number)
            return page.search_for(text, quads=quads)
        return []

    @require_document
    def get_page_images(self, page_number: int) -> List[Tuple]:
        """
        Return a list of all images on a page.

        Args:
            page_number: Number of the page

        Returns:
            List[Tuple]: A list of tuples. Each tuple contains information 
                about an image (xref, smask, etc.).

        Raises:
            PDFDocumentError: If no document is loaded.
        """
        if 0 <= page_number < self.doc.page_count:
            page = self.doc.load_page(page_number)
            return page.get_images()
        return []

    @require_document
    def extract_image(self, xref: int) -> dict:
        """
        Extracts an image from the PDF by its cross-reference number (xref).

        Args:
            xref: Xref number of an image.

        Returns:
            dict: A dictionary containing image metadata and binary image data.

        Raises:
            PDFDocumentError: If no document is loaded.
        """
        return self.doc.extract_image(xref) if self.doc else {}