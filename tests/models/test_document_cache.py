import pytest
import fitz
from src.models.document_cache import DocumentCache

class MockPixmap:
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height

class MockPage:
    def __init__(self, number: int):
        self.number = number

@pytest.fixture
def cache():
    return DocumentCache(max_size=2)

def test_cache_initialization(cache):
    assert cache.max_size == 2
    assert cache.cache_info["size"] == 0
    assert cache.cache_info["max_size"] == 2
    assert cache.cache_info["pages"] == []

def test_add_and_get_page_image(cache):
    page = MockPage(0)
    image = MockPixmap()
    
    # Initially not in cache
    assert cache.get_page_image(page) is None
    
    # Add to cache
    cache.add_page_image(page, image)
    
    # Should be in cache now
    cached_image = cache.get_page_image(page)
    assert cached_image == image
    assert cache.cache_info["size"] == 1
    assert cache.cache_info["pages"] == [0]

def test_cache_eviction(cache):
    # Add three items to a cache with max_size=2
    page1, page2, page3 = MockPage(0), MockPage(1), MockPage(2)
    image1, image2, image3 = MockPixmap(), MockPixmap(), MockPixmap()
    
    cache.add_page_image(page1, image1)
    cache.add_page_image(page2, image2)
    cache.add_page_image(page3, image3)
    
    # First item should be evicted
    assert cache.get_page_image(page1) is None
    assert cache.get_page_image(page2) == image2
    assert cache.get_page_image(page3) == image3
    assert cache.cache_info["size"] == 2
    assert sorted(cache.cache_info["pages"]) == [1, 2]

def test_cache_lru_behavior(cache):
    page1, page2 = MockPage(0), MockPage(1)
    image1, image2 = MockPixmap(), MockPixmap()
    
    cache.add_page_image(page1, image1)
    cache.add_page_image(page2, image2)
    
    # Access page1, making it most recently used
    cache.get_page_image(page1)
    
    # Add new item, should evict page2
    page3 = MockPage(2)
    image3 = MockPixmap()
    cache.add_page_image(page3, image3)
    
    assert cache.get_page_image(page1) == image1  # Still in cache
    assert cache.get_page_image(page2) is None    # Evicted
    assert cache.get_page_image(page3) == image3  # Added
    assert cache.cache_info["size"] == 2
    assert sorted(cache.cache_info["pages"]) == [0, 2]

def test_clear_cache(cache):
    page = MockPage(0)
    image = MockPixmap()
    cache.add_page_image(page, image)
    
    cache.clear()
    assert cache.get_page_image(page) is None
    assert cache.cache_info["size"] == 0
    assert cache.cache_info["pages"] == []

def test_remove_page(cache):
    page1, page2 = MockPage(0), MockPage(1)
    image1, image2 = MockPixmap(), MockPixmap()
    
    cache.add_page_image(page1, image1)
    cache.add_page_image(page1, image2, zoom=2.0)  # Different zoom level
    
    cache.remove_page(0)
    assert cache.get_page_image(page1) is None
    assert cache.get_page_image(page1, zoom=2.0) is None
    assert cache.cache_info["size"] == 0
    assert cache.cache_info["pages"] == []

def test_different_zoom_levels(cache):
    page = MockPage(0)
    image1 = MockPixmap()
    image2 = MockPixmap(200, 200)  # Different size for different zoom
    
    cache.add_page_image(page, image1, zoom=1.0)
    cache.add_page_image(page, image2, zoom=2.0)
    
    assert cache.get_page_image(page, zoom=1.0) == image1
    assert cache.get_page_image(page, zoom=2.0) == image2
    assert cache.cache_info["size"] == 2
    assert cache.cache_info["pages"] == [0]