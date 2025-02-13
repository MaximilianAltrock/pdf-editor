from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QListWidgetItem
from src.views.thumbnail_panel import PDFThumbnailPanel

def create_test_image():
    """Create a test image for thumbnails."""
    img = QImage(100, 100, QImage.Format_RGB888)
    img.fill(Qt.black)
    return QPixmap.fromImage(img)

def test_initial_state(qapp):
    """Test initial panel state."""
    panel = PDFThumbnailPanel()
    assert panel.list_widget.count() == 0
    assert panel.isVisible()
    assert panel.list_widget.iconSize().width() <= 120
    assert panel.list_widget.iconSize().height() <= 160

def test_add_thumbnail(qapp):
    """Test adding thumbnails."""
    panel = PDFThumbnailPanel()
    pixmap = create_test_image()
    panel.add_thumbnail(pixmap, 0)
    
    assert panel.list_widget.count() == 1
    item = panel.list_widget.item(0)
    assert isinstance(item, QListWidgetItem)
    assert item.text() == "Page 1"  # 1-based page numbers in display
    assert not item.icon().isNull()

def test_clear(qapp):
    """Test clearing thumbnails."""
    panel = PDFThumbnailPanel()
    pixmap = create_test_image()
    panel.add_thumbnail(pixmap, 0)
    panel.add_thumbnail(pixmap, 1)
    
    panel.clear()
    assert panel.list_widget.count() == 0

def test_select_page(qapp):
    """Test page selection."""
    panel = PDFThumbnailPanel()
    pixmap = create_test_image()
    panel.add_thumbnail(pixmap, 0)
    panel.add_thumbnail(pixmap, 1)
    
    panel.select_page(1)
    assert panel.list_widget.currentRow() == 1
    
    # Test invalid selection
    panel.select_page(5)  # Beyond range
    assert panel.list_widget.currentRow() == 1  # Should not change

def test_thumbnail_click(qapp, qtbot):
    """Test thumbnail click signal."""
    panel = PDFThumbnailPanel()
    pixmap = create_test_image()
    panel.add_thumbnail(pixmap, 0)
    
    # Connect test slot
    received_signals = []
    panel.pageSelected.connect(lambda page: received_signals.append(page))
    
    # Simulate click
    item = panel.list_widget.item(0)
    panel.list_widget.itemClicked.emit(item)
    
    assert len(received_signals) == 1
    assert received_signals[0] == 0  # Should emit 0-based page number

def test_visibility_toggle(qapp):
    """Test panel visibility toggle."""
    panel = PDFThumbnailPanel()
    assert panel.isVisible()
    panel.setVisible(False)
    assert not panel.isVisible()
    panel.setVisible(True)
    assert panel.isVisible()

def test_multiple_thumbnails(qapp):
    """Test adding multiple thumbnails."""
    panel = PDFThumbnailPanel()
    pixmap = create_test_image()
    num_pages = 5
    
    for i in range(num_pages):
        panel.add_thumbnail(pixmap, i)
    
    assert panel.list_widget.count() == num_pages
    for i in range(num_pages):
        item = panel.list_widget.item(i)
        assert item.text() == f"Page {i + 1}"
        assert not item.icon().isNull()

def test_thumbnail_size_constraints(qapp):
    """Test thumbnail size constraints."""
    panel = PDFThumbnailPanel()
    large_image = QImage(1000, 1000, QImage.Format_RGB888)
    large_image.fill(Qt.black)
    panel.add_thumbnail(QPixmap.fromImage(large_image), 0)
    
    item = panel.list_widget.item(0)
    icon = item.icon()
    actual_size = icon.actualSize(panel.list_widget.iconSize())
    
    assert actual_size.width() <= 120
    assert actual_size.height() <= 160

def test_panel_style(qapp):
    """Test panel styling."""
    panel = PDFThumbnailPanel()
    style = panel.list_widget.styleSheet()
    
    # Check essential style properties
    assert "background-color" in style
    assert "border" in style
    assert "QListWidget::item" in style
    assert "QListWidget::item:selected" in style