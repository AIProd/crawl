"""
Browser pool management for Staff Directory Crawler
Handles browser instances with proper resource management
"""

import asyncio
import gc
import logging
import time
import weakref
from typing import List

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright.sync_api import ViewportSize

from src.config import (
    HEADLESS_MODE, PAGE_TIMEOUT, BROWSER_ARGS,
    USER_AGENT, VIEWPORT_CONFIG
)


class BrowserPool:
    """Manage browser instances with improved resource management"""

    def __init__(self, pool_size: int = 2):
        self.pool_size = pool_size
        self.browsers: List[Browser] = []
        self.contexts: List[BrowserContext] = []
        self.playwright = None
        self.logger = logging.getLogger(__name__)

        # Track active pages with weak references
        self._active_pages = weakref.WeakSet()
        self._active_pages_per_browser = [weakref.WeakSet() for _ in range(pool_size)]
        self._browser_failure_counts = [0] * pool_size
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Initialize browser pool with error handling"""
        try:
            self.playwright = await async_playwright().start()

            for i in range(self.pool_size):
                await self._create_browser_instance(i)

            self.logger.info(f"Initialized browser pool with {self.pool_size} instances")
        except Exception as e:
            self.logger.error(f"Failed to initialize browser pool: {e}")
            await self.close_all()
            raise

    async def _create_browser_instance(self, index: int):
        """Create a single browser instance with context"""
        browser = await self.playwright.chromium.launch(
            headless=HEADLESS_MODE,
            args=BROWSER_ARGS
        )

        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport=ViewportSize(width=VIEWPORT_CONFIG['width'], height=VIEWPORT_CONFIG['height']),
            ignore_https_errors=True,
            bypass_csp=True,
        )

        context.set_default_timeout(PAGE_TIMEOUT)
        context.set_default_navigation_timeout(PAGE_TIMEOUT)

        if len(self.browsers) <= index:
            self.browsers.extend([None] * (index + 1 - len(self.browsers)))
            self.contexts.extend([None] * (index + 1 - len(self.contexts)))

        self.browsers[index] = browser
        self.contexts[index] = context

    async def get_page(self) -> Page:
        """Get a page with load balancing and active page tracking"""
        self.logger.debug(f"get_page called, lock is {'locked' if self._lock.locked() else 'unlocked'}")

        async with self._lock:
            self.logger.debug("Lock acquired in get_page")
            try:

                browser_index = min(
                    range(self.pool_size),
                    key=lambda i: len(self._active_pages_per_browser[i])
                )

                context = self.contexts[browser_index]

                if context.browser and not context.browser.is_connected():
                    self.logger.warning(f"Browser {browser_index} disconnected, restarting...")
                    await self._restart_browser(browser_index)
                    context = self.contexts[browser_index]

                page = await context.new_page()
                page.set_default_timeout(PAGE_TIMEOUT)
                page.set_default_navigation_timeout(PAGE_TIMEOUT)

                self._active_pages.add(page)
                self._active_pages_per_browser[browser_index].add(page)

                page._browser_index = browser_index

                self.logger.debug(
                    f"Created page on browser {browser_index}, active pages: {len(self._active_pages)}"
                )
                return page

            except Exception as e:
                self.logger.error(f"Error getting page: {e}")

                return await self._fallback_page_creation()

    async def _fallback_page_creation(self) -> Page:
        """Fallback method to create a page when primary method fails"""
        for i in range(self.pool_size):
            try:
                if len(self._active_pages_per_browser[i]) == 0:
                    await self._restart_browser(i)
                    context = self.contexts[i]
                    page = await context.new_page()
                    page.set_default_timeout(PAGE_TIMEOUT)
                    page.set_default_navigation_timeout(PAGE_TIMEOUT)

                    self._active_pages.add(page)
                    self._active_pages_per_browser[i].add(page)
                    page._browser_index = i

                    return page
            except Exception:
                continue
        raise Exception("All browsers failed to create pages")

    async def close_page_safely(self, page: Page):
        """Safely close a page with proper tracking cleanup"""
        if page is None:
            return

        browser_index = getattr(page, '_browser_index', 0)

        try:
            if not page.is_closed():
                self.logger.debug(f"Attempting to close page from browser {browser_index}")
                await asyncio.wait_for(page.close(), timeout=5.0)
                self.logger.debug(f"Successfully closed page from browser {browser_index}")
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout closing page from browser {browser_index} - page may be in bad state")
        except Exception as e:
            self.logger.warning(f"Error closing page: {e}")
        finally:
            try:
                self._active_pages.discard(page)
                if browser_index < len(self._active_pages_per_browser):
                    self._active_pages_per_browser[browser_index].discard(page)
            except Exception:
                pass

            self.logger.debug(
                f"Closed page from browser {browser_index}, active pages: {len(self._active_pages)}"
            )

    async def wait_for_all_pages_to_close(self, timeout: float = 30.0):
        """Wait for all active pages to close gracefully"""
        start_time = time.time()
        while len(self._active_pages) > 0:
            if time.time() - start_time > timeout:
                self.logger.warning(f"Timeout waiting for {len(self._active_pages)} pages to close")
                break
            self.logger.info(f"Waiting for {len(self._active_pages)} active pages to close...")
            await asyncio.sleep(1.0)

        if len(self._active_pages) == 0:
            self.logger.info("All pages closed successfully")
        else:
            self.logger.warning(f"{len(self._active_pages)} pages still active after timeout")

    async def _restart_browser(self, index: int):
        """Restart a specific browser instance when safe"""
        try:

            start_time = time.time()
            while len(self._active_pages_per_browser[index]) > 0:
                if time.time() - start_time > 10.0:
                    self.logger.warning(
                        f"Force restarting browser {index} with "
                        f"{len(self._active_pages_per_browser[index])} active pages"
                    )
                    break
                await asyncio.sleep(0.5)

            self.logger.info(f"Restarting browser instance {index}")

            await self._close_browser_instance(index)

            await self._create_browser_instance(index)

            self._browser_failure_counts[index] = 0
            self._active_pages_per_browser[index].clear()

            gc.collect()

        except Exception as e:
            self.logger.error(f"Error restarting browser {index}: {e}")
            self._browser_failure_counts[index] += 1
            raise

    async def _close_browser_instance(self, index: int):
        """Close a specific browser instance"""
        try:
            if index < len(self.contexts) and self.contexts[index]:
                await self.contexts[index].close()
        except Exception:
            pass

        try:
            if index < len(self.browsers) and self.browsers[index]:
                await self.browsers[index].close()
        except Exception:
            pass

    async def close_all(self):
        """Close all browser instances with proper cleanup"""
        try:

            await self.wait_for_all_pages_to_close(timeout=15.0)

            for page in list(self._active_pages):
                await self.close_page_safely(page)

            for context in self.contexts:
                try:
                    if context:
                        await context.close()
                except Exception as e:
                    self.logger.warning(f"Error closing context: {e}")

            for browser in self.browsers:
                try:
                    if browser:
                        await browser.close()
                except Exception as e:
                    self.logger.warning(f"Error closing browser: {e}")

            if self.playwright:
                try:
                    await self.playwright.stop()
                except Exception as e:
                    self.logger.warning(f"Error stopping playwright: {e}")

            self.logger.info("Closed all browser instances")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
        finally:
            self.browsers.clear()
            self.contexts.clear()
            for page_set in self._active_pages_per_browser:
                page_set.clear()
            self._active_pages.clear()
            gc.collect()
