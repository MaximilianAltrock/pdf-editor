import fitz  # PyMuPDF
from typing import List, Tuple, Union

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
        if filepath:
            self.load(filepath)

    def load(self, filepath: str) -> None:
        """
        Loads a PDF document from the specified file path.

        Args:
            filepath (str): The path to the PDF file.

        Raises:
            Exception: If the file cannot be opened.
        """
        try:
            self.doc = fitz.open(filepath)
            self.filepath = filepath
        except Exception:
            raise  # Re-raise for handling in the controller

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
            RuntimeError: If the document is not loaded.
        """
        if self.doc:
            self.doc.save(filepath, garbage=garbage, deflate=deflate, clean=clean)
        else:
             raise RuntimeError("Cannot save: No document loaded.")

    def close(self) -> None:
        """
        Closes the PDF document and releases resources.
        """
        if self.doc:
            self.doc.close()
            self.doc = None
            self.filepath = None

    def get_page_count(self) -> int:
        """
        Gets the total number of pages in the document.

        Returns:
            int: The number of pages.
        """
        return self.doc.page_count if self.doc else 0

    def get_metadata(self) -> dict:
        """
        Retrieves the document's metadata.

        Returns:
             dict: A dictionary containing the document's metadata.  Returns
                an empty dictionary if no document is loaded.
        """
        return self.doc.metadata if self.doc else {}
    
    def get_toc(self, simple: bool = True) -> List[List]:
        """
        Retrieves the table of contents (TOC).

        Args:
            simple: Whether to get a simplified TOC of only 3 items

        Returns:
            list: The table of contents as a list of lists.  Each inner list
            represents a TOC entry. Returns an empty list if no document is loaded.
        """
        return self.doc.get_toc(simple=simple) if self.doc else []
    
    def delete_page(self, page_number: int) -> None:
        """
        Deletes a page from the document.

        Args:
            page_number (int): The zero-based index of the page to delete.

        Raises:
            IndexError: If the page number is out of range.
            RuntimeError: If no document is loaded.
        """
        if not self.doc:
            raise RuntimeError("Cannot delete page: No document loaded.")
        
        if 0 <= page_number < self.doc.page_count:
            self.doc.delete_page(page_number)
        else:
            raise IndexError("Page number out of range.")

    def delete_pages(self, from_page: int, to_page: int) -> None:
        """
        Deletes a range of pages from the document.

        Args:
            from_page (int): The zero-based index of the first page to delete
                (inclusive).
            to_page (int): The zero-based index of the last page to delete
                (inclusive).

        Raises:
            IndexError: If the page numbers are out of range.
            RuntimeError: If no document is loaded.
        """
        if not self.doc:
            raise RuntimeError("Cannot delete pages: No document loaded.")
            
        if 0 <= from_page <= to_page < self.doc.page_count:
             self.doc.delete_pages(from_page=from_page, to_page=to_page)
        else:
            raise IndexError("Page numbers out of range.")
    
    def move_page(self, from_page: int, to_page: int) -> None:
        """
        Moves a page within the document.

        Args:
            from_page (int): The zero-based index of the page to move.
            to_page (int): The zero-based index. The page will be inserted BEFORE 
                this position due to PyMuPDF's default behavior.
        
        Raises:
            IndexError: If the page numbers are out of range.
            RuntimeError: If no document is loaded.
        """
        if not self.doc:
            raise RuntimeError("Cannot move page: No document loaded.")
        
        if 0 <= from_page < self.doc.page_count and 0 <= to_page < self.doc.page_count:
            self.doc.move_page(from_page, to_page)
        else:
            raise IndexError("Page number out of range.")
        
        
    def copy_page(self, page_number: int, to_page: int = -1) -> None:
        """
        Copy a page within the document.

        Args:
            page_number (int): The zero-based index of the page to copy.
            to_page (int): The zero-based index where the page should be copied to.
                If -1, copy to end of the document

        Raises:
            IndexError: If the page numbers are out of range.
            RuntimeError: If no document is loaded.
        """
        if not self.doc:
            raise RuntimeError("Cannot copy page: No document loaded.")
        
        if 0 <= page_number < self.doc.page_count:
            self.doc.copy_page(page_number, to_page)
        else:
            raise IndexError("Page number out of range.")

    def select(self, page_list: List[int]) -> None:
        """
        Selects a subset of pages to keep in the document, removing all others.

        Args:
            page_list (list[int]):  A list of zero-based page numbers to keep.
                The order of page numbers in the list determines the new order
                of pages in the document.  Pages can be repeated.

        Raises:
            ValueError: If any page number in the list is out of range.
            RuntimeError: If no document is loaded.
        """
        if not self.doc:
            raise RuntimeError("Cannot select pages: No document loaded.")

        if all(0 <= p < self.doc.page_count for p in page_list):
            self.doc.select(page_list)
        else:
            raise ValueError("Invalid page number(s) in selection list.")

    def new_page(self, pno: int = -1, width: float = -1, height: float = -1) -> fitz.Page:
        """
        Creates a new page in the PDF.

        Args:
            pno: Where to insert: -1 means at the end (default) like Python.
                Supports insertion in front of 0.
            width: page width.
            height: page height.

        Returns:
            fitz.Page: The new page object, or None if failed.

        Raises:
            RuntimeError: If no document is loaded.
        """
        if not self.doc:
            raise RuntimeError("Cannot add new page: No document loaded.")
            
        return self.doc.new_page(pno=pno, width=width, height=height)

    def get_page_image(self, page_number: int, zoom: float = 1.0) -> fitz.Pixmap | None:
        """
        Gets a QPixmap representation of a page for display.

        Args:
            page_number (int): The zero-based index of the page.
            zoom (float): The zoom factor. Defaults to 1.0.

        Returns:
            fitz.Pixmap | None:  A Pixmap object representing the page image,
                or None if the page number is invalid or no document loaded.
        """
        if self.doc and 0 <= page_number < self.doc.page_count:
            page = self.doc.load_page(page_number)
            matrix = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=matrix)
            return pix
        return None
    
    def get_page_text(self, page_number: int, text_type: str = "text") -> str:
        """
        Gets text from page

        Args:
            page_number: Number of the page.
            text_type: Type of the text. "text" | "blocks" | "words" | "html" | "dict" | "json" | "rawdict" | "rawjson" | "xhtml" | "xml"

        Returns:
            str | None: Text of the page as string, or None if the page number is
                invalid or no document loaded.
        """
        
        if self.doc and 0 <= page_number < self.doc.page_count:
            page = self.doc.load_page(page_number)
            return page.get_text(text_type)
        return None
    
    def search_page_for(self, page_number: int, text: str, quads: bool = False) -> List[Union[fitz.Rect, fitz.Quad]]:
        """
        Searches text on a page.

        Args:
            page_number: Number of the page.
            text: Text for searching
            quads: return quads instead of rectangles.

        Returns:
            list[fitz.Rect] | list[fitz.Quad] | None: If quads is False a list of fitz.Rect
                objects each surrounding a found occurrence. If quads is True, a list of fitz.Quad.
        """
        if self.doc and 0 <= page_number < self.doc.page_count:
            page = self.doc.load_page(page_number)
            return page.search_for(text, quads=quads)
        return None

    def get_page_images(self, page_number: int) -> List[Tuple]:
        """
        Return a list of all images on a page.

        Args:
            page_number: Number of the page

        Returns:
            list[tuple]: A list of tuples.
            Each tuple contains information about an image (xref, smask, ...).
            Returns an empty list if no images are found, the page number is invalid,
            or no document is loaded.
        """
        if self.doc and 0 <= page_number < self.doc.page_count:
            page = self.doc.load_page(page_number)
            return page.get_images()
        return []

    def extract_image(self, xref: int) -> dict:
        """
        Extracts an image from the PDF by its cross-reference number (xref).

        Args:
            xref: Xref number of an image.

        Returns:
             dict: A dictionary containing image metadata and the binary image
            data, or an empty dictionary if no image is found for the given xref or
            no document loaded.
        """
        return self.doc.extract_image(xref) if self.doc else {}