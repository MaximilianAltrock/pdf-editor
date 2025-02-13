"""
Cache implementation for PDF document resources like page images and thumbnails.
"""
from typing import Optional, Dict
import fitz
from collections import OrderedDict
from threading import Lock

class DocumentCache:
    """
    Handles caching of document resources like page images and thumbnails.
    Implements an LRU (Least Recently Used) cache with thread-safe operations.
    """
    def __init__(self, max_size: int = 100):
        """
        Initialize the document cache.
        
        Args:
            max_size: Maximum number of items to keep in cache
        """
        self.max_size = max_size
        self._page_cache: OrderedDict[tuple, fitz.Pixmap] = OrderedDict()
        self._cache_lock = Lock()
        
    def get_page_image(self, page: fitz.Page, zoom: float = 1.0) -> Optional[fitz.Pixmap]:
        """
        Get a cached page image if available, otherwise return None.
        
        Args:
            page: The page to get the image for
            zoom: The zoom factor for the page image
            
        Returns:
            The cached Pixmap if available, otherwise None
        """
        # Round zoom to 2 decimal places to prevent nearly identical cache entries
        zoom = round(zoom, 2)
        cache_key = (page.number, zoom)
        
        with self._cache_lock:
            if cache_key in self._page_cache:
                # Move to end to mark as recently used
                self._page_cache.move_to_end(cache_key)
                return self._page_cache[cache_key]
        return None
        
    def add_page_image(self, page: fitz.Page, image: fitz.Pixmap, zoom: float = 1.0) -> None:
        """
        Add a page image to the cache.
        
        Args:
            page: The page the image is for
            image: The page image to cache
            zoom: The zoom factor for the page image
        """
        # Round zoom to 2 decimal places to prevent nearly identical cache entries
        zoom = round(zoom, 2)
        cache_key = (page.number, zoom)
        
        with self._cache_lock:
            # If already in cache, don't add again
            if cache_key in self._page_cache:
                return
                
            # If cache is full, remove oldest item
            if len(self._page_cache) >= self.max_size:
                self._page_cache.popitem(last=False)
            
            self._page_cache[cache_key] = image
            
    def clear(self) -> None:
        """Clear all cached items."""
        with self._cache_lock:
            self._page_cache.clear()
            
    def remove_page(self, page_number: int) -> None:
        """
        Remove all cached items for a specific page.
        
        Args:
            page_number: The page number to remove items for
        """
        with self._cache_lock:
            keys_to_remove = [k for k in self._page_cache.keys() 
                            if k[0] == page_number]
            for key in keys_to_remove:
                del self._page_cache[key]

    @property
    def cache_info(self) -> Dict:
        """
        Get information about the cache state.
        
        Returns:
            A dictionary with cache statistics
        """
        with self._cache_lock:
            return {
                "size": len(self._page_cache),
                "max_size": self.max_size,
                "pages": sorted(list(set(k[0] for k in self._page_cache.keys())))
            }