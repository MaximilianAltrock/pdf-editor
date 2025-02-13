from src.views.toolbar import PDFToolBar

def test_initial_state(qapp):
    """Test initial toolbar state."""
    toolbar = PDFToolBar()
    
    # Test basic properties
    assert not toolbar.isMovable()
    assert toolbar.iconSize().width() == 24
    assert toolbar.iconSize().height() == 24
    
    # Test page navigation controls
    assert toolbar.pageSpinBox.minimum() == 1
    assert toolbar.pageSpinBox.maximum() == 1
    assert toolbar.pageSpinBox.value() == 1
    assert toolbar.totalPagesLabel.text() == " / 1"
    
    # Test initial action states (should be disabled)
    assert not toolbar.saveAction.isEnabled()
    assert not toolbar.saveAsAction.isEnabled()
    assert not toolbar.zoomInAction.isEnabled()
    assert not toolbar.zoomOutAction.isEnabled()
    assert not toolbar.zoomResetAction.isEnabled()
    assert not toolbar.previousPageAction.isEnabled()
    assert not toolbar.nextPageAction.isEnabled()
    assert not toolbar.pageSpinBox.isEnabled()

def test_action_enable_disable(qapp):
    """Test enabling and disabling actions."""
    toolbar = PDFToolBar()
    
    toolbar.update_actions(True)  # Document loaded
    assert all(action.isEnabled() for action in [
        toolbar.saveAction,
        toolbar.saveAsAction,
        toolbar.zoomInAction,
        toolbar.zoomOutAction,
        toolbar.zoomResetAction,
        toolbar.previousPageAction,
        toolbar.nextPageAction,
        toolbar.pageSpinBox
    ])
    
    toolbar.update_actions(False)  # Document unloaded
    assert not any(action.isEnabled() for action in [
        toolbar.saveAction,
        toolbar.saveAsAction,
        toolbar.zoomInAction,
        toolbar.zoomOutAction,
        toolbar.zoomResetAction,
        toolbar.previousPageAction,
        toolbar.nextPageAction,
        toolbar.pageSpinBox
    ])

def test_page_navigation_updates(qapp):
    """Test page navigation control updates."""
    toolbar = PDFToolBar()
    toolbar.update_actions(True)  # Enable controls
    
    # Test first page
    toolbar.update_page_info(0, 5)  # page 1 of 5
    assert toolbar.pageSpinBox.value() == 1
    assert toolbar.pageSpinBox.maximum() == 5
    assert toolbar.totalPagesLabel.text() == " / 5"
    assert not toolbar.previousPageAction.isEnabled()  # No previous page
    assert toolbar.nextPageAction.isEnabled()  # Has next page
    
    # Test middle page
    toolbar.update_page_info(2, 5)  # page 3 of 5
    assert toolbar.pageSpinBox.value() == 3
    assert toolbar.previousPageAction.isEnabled()  # Has previous page
    assert toolbar.nextPageAction.isEnabled()  # Has next page
    
    # Test last page
    toolbar.update_page_info(4, 5)  # page 5 of 5
    assert toolbar.pageSpinBox.value() == 5
    assert toolbar.previousPageAction.isEnabled()  # Has previous page
    assert not toolbar.nextPageAction.isEnabled()  # No next page

def test_page_spinbox_signals(qapp):
    """Test page spinbox signals."""
    toolbar = PDFToolBar()
    toolbar.update_actions(True)
    toolbar.update_page_info(0, 5)  # Set up 5 pages
    
    # Track emitted signals
    received_pages = []
    toolbar.pageRequested.connect(lambda page: received_pages.append(page))
    
    # Change page number directly
    toolbar.pageSpinBox.setValue(3)
    assert len(received_pages) == 1
    assert received_pages[0] == 2  # Convert to 0-based index

def test_navigation_button_signals(qapp):
    """Test navigation button signals."""
    toolbar = PDFToolBar()
    toolbar.update_actions(True)
    toolbar.update_page_info(1, 5)  # Start at page 2 of 5
    
    # Track emitted signals
    signals_received = []
    toolbar.previousPageRequested.connect(
        lambda: signals_received.append("previous")
    )
    toolbar.nextPageRequested.connect(
        lambda: signals_received.append("next")
    )
    
    toolbar.previousPageAction.trigger()
    toolbar.nextPageAction.trigger()
    
    assert signals_received == ["previous", "next"]

def test_zoom_button_signals(qapp):
    """Test zoom button signals."""
    toolbar = PDFToolBar()
    toolbar.update_actions(True)
    
    # Track emitted signals
    signals_received = []
    toolbar.zoomInRequested.connect(
        lambda: signals_received.append("zoom_in")
    )
    toolbar.zoomOutRequested.connect(
        lambda: signals_received.append("zoom_out")
    )
    toolbar.zoomResetRequested.connect(
        lambda: signals_received.append("zoom_reset")
    )
    
    toolbar.zoomInAction.trigger()
    toolbar.zoomOutAction.trigger()
    toolbar.zoomResetAction.trigger()
    
    assert signals_received == ["zoom_in", "zoom_out", "zoom_reset"]

def test_file_operation_signals(qapp):
    """Test file operation signals."""
    toolbar = PDFToolBar()
    toolbar.update_actions(True)
    
    # Track emitted signals
    signals_received = []
    toolbar.fileOpenRequested.connect(
        lambda: signals_received.append("open")
    )
    toolbar.fileSaveRequested.connect(
        lambda: signals_received.append("save")
    )
    toolbar.fileSaveAsRequested.connect(
        lambda: signals_received.append("save_as")
    )
    
    toolbar.openAction.trigger()
    toolbar.saveAction.trigger()
    toolbar.saveAsAction.trigger()
    
    assert signals_received == ["open", "save", "save_as"]

def test_style_properties(qapp):
    """Test toolbar styling."""
    toolbar = PDFToolBar()
    
    # Test spinbox style properties
    spinbox_style = toolbar.pageSpinBox.styleSheet()
    assert "background-color" in spinbox_style
    assert "color" in spinbox_style
    assert "border" in spinbox_style
    
    # Test label style properties
    label_style = toolbar.totalPagesLabel.styleSheet()
    assert "color" in label_style
    assert "padding" in label_style