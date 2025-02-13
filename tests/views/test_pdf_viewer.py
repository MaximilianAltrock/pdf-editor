import pytest
from PySide6.QtCore import Qt, QPoint, QPointF
from PySide6.QtGui import QImage, QWheelEvent
from src.views.pdf_viewer import PDFViewerWidget, PDFPageLabel

def test_initial_state(qapp):
    """Test initial viewer state."""
    viewer = PDFViewerWidget()
    assert viewer.current_page == 0
    assert viewer.total_pages == 0
    assert viewer.zoom_level == 1.0
    assert len(viewer.page_labels) == 0

def test_zoom_limits(qapp):
    """Test zoom level limits."""
    viewer = PDFViewerWidget()
    viewer.set_zoom(0.05)  # Below minimum
    assert viewer.zoom_level == 0.1  # Should be clamped to minimum
    
    viewer.set_zoom(6.0)  # Above maximum
    assert viewer.zoom_level == 5.0  # Should be clamped to maximum

def test_set_document(qapp):
    """Test document initialization."""
    viewer = PDFViewerWidget()
    
    # Track signals
    pages_changed = []
    viewer.pageChanged.connect(lambda page: pages_changed.append(page))
    
    total_pages = 5
    viewer.set_document(total_pages)
    
    assert viewer.total_pages == total_pages
    assert len(viewer.page_labels) == total_pages
    assert all(isinstance(label, PDFPageLabel) for label in viewer.page_labels)
    assert pages_changed == [0]  # Should emit initial page

def test_page_navigation(qapp):
    """Test page navigation."""
    viewer = PDFViewerWidget()
    viewer.set_document(5)
    
    # Track emitted signals
    received_pages = []
    viewer.pageChanged.connect(lambda page: received_pages.append(page))
    received_pages.clear()  # Clear initial signal
    
    assert viewer.go_to_page(2)  # Valid page
    assert viewer.current_page == 2
    assert received_pages == [2]
    
    assert not viewer.go_to_page(10)  # Invalid page
    assert viewer.current_page == 2  # Should not change
    assert len(received_pages) == 1  # No new signal

def test_zoom_operations(qapp):
    """Test zoom operations."""
    viewer = PDFViewerWidget()
    initial_zoom = viewer.zoom_level
    
    viewer.zoom_in()
    assert viewer.zoom_level > initial_zoom
    
    viewer.zoom_out()
    assert viewer.zoom_level == pytest.approx(initial_zoom, rel=1e-10)
    
    viewer.reset_zoom()
    assert viewer.zoom_level == 1.0

def test_page_display(qapp):
    """Test page display."""
    viewer = PDFViewerWidget()
    # Create test image
    img = QImage(100, 100, QImage.Format_RGB888)
    img.fill(Qt.black)
    
    viewer.set_document(1)
    viewer.display_page(0, img)
    
    assert viewer.page_labels[0].pixmap() is not None

def test_clear(qapp):
    """Test clearing the viewer."""
    viewer = PDFViewerWidget()
    viewer.set_document(3)
    viewer.clear()
    
    assert viewer.total_pages == 0
    assert viewer.current_page == 0
    assert len(viewer.page_labels) == 0

def test_wheel_zoom(qapp):
    """Test zooming with mouse wheel."""
    viewer = PDFViewerWidget()
    initial_zoom = viewer.zoom_level
    
    # Create wheel event with Ctrl modifier
    event = QWheelEvent(
        QPointF(50, 50),  # pos
        QPointF(50, 50),  # global pos
        QPoint(0, 0),     # pixelDelta
        QPoint(0, 120),   # angleDelta
        Qt.MouseButton.NoButton,  # buttons
        Qt.KeyboardModifier.ControlModifier,  # modifiers
        Qt.ScrollPhase.NoScrollPhase,  # phase
        False,            # inverted
        Qt.MouseEventSource.MouseEventNotSynthesized  # source
    )
    
    # Process the event
    viewer.wheelEvent(event)
    assert viewer.zoom_level > initial_zoom

def test_scroll_page_tracking(qapp):
    """Test page tracking during scrolling."""
    viewer = PDFViewerWidget()
    viewer.set_document(3)
    
    # Track page change signals
    received_pages = []
    viewer.pageChanged.connect(lambda page: received_pages.append(page))
    received_pages.clear()  # Clear initial signal
    
    # Mock scroll position changes
    viewer._on_scroll_changed()
    assert viewer.current_page == 0  # Should start at first page
    assert received_pages == []  # No change from last known page, no signal needed