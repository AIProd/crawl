"""Job for extracting data from individual profile pages.

This job loads a staff member's profile page and retrieves the profile image
URL and bio text.  The implementation relies on Playwright for page loading and
DOM inspection, matching the rest of the crawler infrastructure.
"""

from dataclasses import dataclass
import re
from typing import Optional

from playwright.async_api import Page

from src.jobs.base_job import BaseJob
from src.models import StaffMember
from src.utils import _load_page, make_full_url


@dataclass
class ProfileJob(BaseJob):
    """Process a single staff profile page"""

    async def process(self, page: Page) -> StaffMember:
        """Load the profile page and extract image URL and biography"""

        url = self.data.get("profile_link") or self.data.get("url")
        if not url:
            raise Exception("Profile URL missing")

        await _load_page(page, url)

        image_url = await self._extract_image(page, url)
        bio_text = await self._extract_bio(page)

        data = self.data.copy()
        data["profile_image_link"] = image_url
        data["bio"] = bio_text

        return StaffMember(**data)

    async def _extract_image(self, page: Page, page_url: str) -> Optional[str]:
        """Extract profile image URL from page"""

        selector = (
            "div.sidearm-staff-member-bio-image img, "
            "div.sidearm-common-bio-image img"
        )

        try:
            img = page.locator(selector).first
            if await img.count() > 0:
                src = await img.get_attribute("src")
                if src:
                    return make_full_url(src, page_url)
        except Exception:
            pass

        try:
            og = page.locator("meta[property='og:image']").first
            if await og.count() > 0:
                content = await og.get_attribute("content")
                if content:
                    return content
        except Exception:
            pass

        return None

    async def _extract_bio(self, page: Page) -> str:
        """Extract biography text from page"""

        locator = page.locator("div.sidearm-common-bio-full").first
        try:
            if await locator.count() == 0:
                return ""

            html = await locator.inner_html()
            html = re.sub(r"(?i)<br\s*/?>", "\n", html)
            text = re.sub(r"<[^>]+>", "", html)
            text = re.sub(r"\s+\n", "\n", text)
            return text.strip()
        except Exception:
            return ""

