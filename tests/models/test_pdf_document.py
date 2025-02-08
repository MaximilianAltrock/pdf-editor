import pytest
from src.models.pdf_document import PDFDocument
import fitz
import os
from typing import List

# Fixture for creating a temporary PDF file
@pytest.fixture
def temp_pdf(tmp_path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "Test Page", fontsize=12)
    filepath = tmp_path / "test.pdf"
    doc.save(str(filepath))
    doc.close()
    yield str(filepath)
    if os.path.exists(str(filepath)):
        os.remove(str(filepath))

# Fixture for a PDF with multiple pages
@pytest.fixture
def multi_page_pdf(tmp_path):
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((50, 72), f"Page {i+1}", fontsize=12)
    filepath = tmp_path / "multi_page.pdf"
    doc.save(str(filepath))
    doc.close()
    yield str(filepath)
    if os.path.exists(str(filepath)):
        os.remove(str(filepath))

# --- Tests for existing methods ---

def test_load_pdf(temp_pdf):
    doc = PDFDocument(temp_pdf)
    assert doc.doc is not None
    assert doc.get_page_count() == 1
    assert doc.filepath == temp_pdf
    doc.close()

def test_save_pdf(temp_pdf, tmp_path):
    doc = PDFDocument(temp_pdf)
    new_filepath = tmp_path / "new_test.pdf"
    doc.save(str(new_filepath))
    assert new_filepath.exists()
    doc.close()
    doc2 = fitz.open(str(new_filepath))
    assert doc2.page_count == 1
    doc2.close()

def test_save_no_doc_loaded(tmp_path):
    doc = PDFDocument()
    with pytest.raises(RuntimeError):
        doc.save(tmp_path / "fail.pdf")

def test_close_pdf(temp_pdf):
    doc = PDFDocument(temp_pdf)
    doc.close()
    assert doc.doc is None
    assert doc.filepath is None

def test_delete_page(temp_pdf):
    doc = PDFDocument(temp_pdf)
    doc.delete_page(0)
    assert doc.get_page_count() == 0
    doc.close()

def test_delete_page_invalid_index(temp_pdf):
    doc = PDFDocument(temp_pdf)
    with pytest.raises(IndexError):
        doc.delete_page(1)
    doc.close()

def test_delete_page_no_document_loaded(temp_pdf):
    doc = PDFDocument()
    with pytest.raises(RuntimeError):
        doc.delete_page(0)

def test_get_page_image(temp_pdf):
    doc = PDFDocument(temp_pdf)
    pixmap = doc.get_page_image(0)
    assert pixmap is not None
    assert isinstance(pixmap, fitz.Pixmap)
    doc.close()

def test_get_page_image_invalid_index(temp_pdf):
    doc = PDFDocument(temp_pdf)
    pixmap = doc.get_page_image(1)
    assert pixmap is None
    doc.close()

def test_load_nonexistent_pdf():
    with pytest.raises(Exception):
        PDFDocument("nonexistent.pdf")

# --- Tests for new methods ---

def test_get_metadata(temp_pdf):
    doc = PDFDocument(temp_pdf)
    metadata = doc.get_metadata()
    assert isinstance(metadata, dict)
    assert "producer" in metadata
    doc.close()
    
def test_get_metadata_no_doc(temp_pdf):
    doc = PDFDocument()
    metadata = doc.get_metadata()
    assert isinstance(metadata, dict)
    assert len(metadata) == 0
    doc.close()

def test_get_toc(temp_pdf):
    doc = PDFDocument(temp_pdf)
    toc = doc.get_toc()
    assert isinstance(toc, list)
    if doc.doc:
        doc.doc.set_toc([ [1, "Chapter 1", 1] ])
        toc = doc.get_toc()
    assert len(toc) > 0 if doc.doc else len(toc) == 0
    doc.close()
    
def test_get_toc_no_doc(temp_pdf):
    doc = PDFDocument()
    toc = doc.get_toc()
    assert isinstance(toc, list)
    assert len(toc) == 0
    doc.close()

def test_delete_pages(multi_page_pdf):
    doc = PDFDocument(multi_page_pdf)
    doc.delete_pages(1, 1)
    assert doc.get_page_count() == 2
    assert doc.get_page_text(0) == "Page 1\n"
    assert doc.get_page_text(1) == "Page 3\n"
    doc.close()

def test_delete_pages_invalid_range(multi_page_pdf):
    doc = PDFDocument(multi_page_pdf)
    with pytest.raises(IndexError):
        doc.delete_pages(1, 3)
    with pytest.raises(IndexError):
        doc.delete_pages(2, 1)
    doc.close()

def test_delete_pages_no_document_loaded():
    doc = PDFDocument()
    with pytest.raises(RuntimeError):
        doc.delete_pages(0,1)

def test_move_page(multi_page_pdf):
    doc = PDFDocument(multi_page_pdf)
    doc.move_page(0, 2)  # Move page 0 to *before* index 2.

    assert doc.get_page_count() == 3
    assert doc.get_page_text(0) == "Page 2\n"
    assert doc.get_page_text(1) == "Page 1\n"
    assert doc.get_page_text(2) == "Page 3\n"
    doc.close()

def test_move_page_invalid_index(multi_page_pdf):
    doc = PDFDocument(multi_page_pdf)
    with pytest.raises(IndexError):
        doc.move_page(0, 3)
    doc.close()

def test_move_page_no_document_loaded():
    doc = PDFDocument()
    with pytest.raises(RuntimeError):
        doc.move_page(0,1)

def test_copy_page(multi_page_pdf):
    doc = PDFDocument(multi_page_pdf)
    doc.copy_page(0) #copy to end
    assert doc.get_page_count() == 4
    assert doc.get_page_text(0) == "Page 1\n"
    assert doc.get_page_text(3) == "Page 1\n"
    doc.close()

def test_copy_page_to_position(multi_page_pdf):
    doc = PDFDocument(multi_page_pdf)
    doc.copy_page(0, 1) #copy to position
    assert doc.get_page_count() == 4
    assert doc.get_page_text(0) == "Page 1\n"
    assert doc.get_page_text(1) == "Page 1\n"
    assert doc.get_page_text(2) == "Page 2\n"
    doc.close()

def test_copy_page_invalid_index(multi_page_pdf):
    doc = PDFDocument(multi_page_pdf)
    with pytest.raises(IndexError):
        doc.copy_page(3)
    doc.close()

def test_copy_page_no_document_loaded():
    doc = PDFDocument()
    with pytest.raises(RuntimeError):
        doc.copy_page(0)
        
def test_select(multi_page_pdf):
    doc = PDFDocument(multi_page_pdf)
    doc.select([1, 0, 1])
    assert doc.get_page_count() == 3
    assert doc.get_page_text(0) == "Page 2\n"
    assert doc.get_page_text(1) == "Page 1\n"
    assert doc.get_page_text(2) == "Page 2\n"
    doc.close()

def test_select_invalid_page_list(multi_page_pdf):
    doc = PDFDocument(multi_page_pdf)
    with pytest.raises(ValueError):
        doc.select([0, 3, 1])
    doc.close()

def test_select_no_document_loaded():
    doc = PDFDocument()
    with pytest.raises(RuntimeError):
        doc.select([0, 1])

def test_new_page(temp_pdf):
    doc = PDFDocument(temp_pdf)
    new_page = doc.new_page()
    assert doc.get_page_count() == 2
    assert new_page is not None
    assert isinstance(new_page, fitz.Page)
    doc.close()
    
def test_new_page_with_int(temp_pdf):
    doc = PDFDocument(temp_pdf)
    new_page = doc.new_page(pno=0, width=100, height=200)
    assert doc.get_page_count() == 2
    assert new_page is not None
    assert isinstance(new_page, fitz.Page)
    doc.close()

def test_new_page_no_document_loaded():
    doc = PDFDocument()
    with pytest.raises(RuntimeError):
        doc.new_page()

def test_get_page_text(temp_pdf):
    doc = PDFDocument(temp_pdf)
    text = doc.get_page_text(0)
    assert "Test Page" in text
    doc.close()

def test_get_page_text_html(temp_pdf):
    doc = PDFDocument(temp_pdf)
    text = doc.get_page_text(0, "html")
    assert "<span" in text and "Test Page" in text
    doc.close()
    
def test_get_page_text_invalid_page(temp_pdf):
    doc = PDFDocument(temp_pdf)
    text = doc.get_page_text(1)
    assert text is None
    doc.close()

def test_get_page_text_no_document_loaded():
    doc = PDFDocument()
    text = doc.get_page_text(0)
    assert text is None

def test_search_page_for(temp_pdf):
    doc = PDFDocument(temp_pdf)
    results: List[fitz.Rect] = doc.search_page_for(0, "Test")
    assert len(results) == 1
    assert isinstance(results[0], fitz.Rect)
    doc.close()

def test_search_page_for_quads(temp_pdf):
    doc = PDFDocument(temp_pdf)
    results: List[fitz.Quad] = doc.search_page_for(0, "Test", quads=True)
    assert len(results) == 1
    assert isinstance(results[0], fitz.Quad)
    doc.close()

def test_search_page_for_not_found(temp_pdf):
    doc = PDFDocument(temp_pdf)
    results = doc.search_page_for(0, "Nonexistent")
    assert len(results) == 0
    doc.close()

def test_search_page_for_invalid_page(temp_pdf):
    doc = PDFDocument(temp_pdf)
    results = doc.search_page_for(1, "Test")
    assert results is None
    doc.close()
    
def test_search_page_for_no_document_loaded():
    doc = PDFDocument()
    results = doc.search_page_for(0, "Test")
    assert results is None

def test_get_page_images(temp_pdf):
    doc = PDFDocument(temp_pdf)
    page = doc.doc.load_page(0)
    rect = fitz.Rect(0, 0, 100, 100)
    page.insert_image(rect, filename = "resources/icons/open.png")
    
    images = doc.get_page_images(0)
    assert isinstance(images, list)
    assert len(images) > 0

    doc.close()

def test_get_page_images_invalid_page(temp_pdf):
    doc = PDFDocument(temp_pdf)
    images = doc.get_page_images(1)
    assert len(images) == 0
    doc.close()

def test_get_page_images_no_document_loaded():
    doc = PDFDocument()
    images = doc.get_page_images(0)
    assert len(images) == 0

def test_extract_image(temp_pdf):
    doc = PDFDocument(temp_pdf)
    page = doc.doc.load_page(0)
    rect = fitz.Rect(0, 0, 100, 100)
    page.insert_image(rect, filename = "resources/icons/open.png")
    images = doc.get_page_images(0)
    if images:
        xref = images[0][0]
        image_data = doc.extract_image(xref)
        assert isinstance(image_data, dict)
        assert "ext" in image_data
        assert "image" in image_data
    doc.close()

def test_extract_image_no_document_loaded():
    doc = PDFDocument()
    image = doc.extract_image(1)
    assert len(image) == 0