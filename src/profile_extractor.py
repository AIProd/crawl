"""
Profile data extraction for Staff Directory Crawler
Updated to work with unified BaseJob system
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

from playwright.async_api import Page

from src.config import BROWSER_TIMEOUT
from src.jobs.base_job import BaseJob
from src.models import StaffMember
from src.utils import make_full_url


class ProfileExtractor:
    """Extract data from individual staff profile pages"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    async def extract_profile_data(self, job: BaseJob, page: Page) -> Dict[str, Any]:
        """Extract data from a staff member's profile page"""
        job_data = job.data
        staff_name = job_data.get('name', '')
        self.logger.info(f"Extracting profile data for {staff_name}")

        await self._load_profile_page(job, page)

        profile_data: Dict[str, Any] = {}

        try:
            image_url = await self._extract_profile_image(page, job_data.get('profile_link') or job_data.get('url'))
            if image_url:
                profile_data['profile_image_link'] = image_url

            paragraphs = await self._extract_page_paragraphs(page)
            if paragraphs:
                profile_data['bio'] = max(paragraphs, key=len)

        except Exception as e:
            self.logger.warning(f"Error extracting profile data for {staff_name}: {e}")
            return {}

        self.logger.info(
            f"Profile extraction completed for {staff_name}: {len(profile_data)} data categories extracted")

        return profile_data

    async def _load_profile_page(self, job: BaseJob, page: Page):
        """Load the profile page with error handling"""
        url = job.data.get('profile_link') or job.data.get('url')
        try:
            response = await asyncio.wait_for(
                page.goto(url, timeout=BROWSER_TIMEOUT, wait_until='domcontentloaded'),
                timeout=BROWSER_TIMEOUT / 1000
            )
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
        except asyncio.TimeoutError:
            raise Exception("Timeout loading profile page")
        except Exception as e:
            raise Exception(f"Failed to load profile page: {str(e)}")

    async def _extract_page_paragraphs(self, page: Page) -> List[str]:
        """Extract all text content from the page, prioritizing bio/info/profile sections"""
        paragraphs = []
        bio_paragraphs = []

        try:
            bio_selectors = [
                'div[class*="bio"] p',
                'div[class*="info"] p',
                'div[class*="profile"] p',
                'section[class*="bio"] p',
                'section[class*="info"] p',
                'section[class*="profile"] p',
                '[class*="biography"] p',
                '[class*="about"] p'
            ]

            for selector in bio_selectors:
                try:
                    bio_elements = await asyncio.wait_for(page.locator(selector).all(), timeout=3.0)
                    for element in bio_elements:
                        try:
                            text = await asyncio.wait_for(element.text_content(), timeout=2.0)
                            if text and len(text.strip()) > 20:
                                bio_paragraphs.append(text.strip())
                        except:
                            continue
                except:
                    continue

            if bio_paragraphs:
                bio_paragraphs.sort(key=len, reverse=True)
                paragraphs.extend(bio_paragraphs[:10])

            if not paragraphs:
                paragraph_elements = await asyncio.wait_for(page.locator('p').all(), timeout=5.0)
                for element in paragraph_elements[:20]:
                    try:
                        text = await asyncio.wait_for(element.text_content(), timeout=2.0)
                        if text and len(text.strip()) > 20:
                            paragraphs.append(text.strip())
                    except:
                        continue

                paragraphs.sort(key=len, reverse=True)

        except Exception as e:
            self.logger.debug(f"Error extracting page text: {e}")

        return paragraphs

    async def _extract_profile_image(self, page: Page, page_url: str | None) -> Optional[str]:
        """Extract profile image URL using common selectors"""
        if not page_url:
            page_url = ''

        selector = (
            "div.sidearm-staff-member-bio-image img, "
            "div.sidearm-common-bio-image img"
        )

        try:
            img = page.locator(selector).first
            if await img.count() > 0:
                src = await img.get_attribute('src')
                if src:
                    return make_full_url(src, page_url)
        except Exception:
            pass

        try:
            og = page.locator("meta[property='og:image']").first
            if await og.count() > 0:
                content = await og.get_attribute('content')
                if content:
                    return content
        except Exception:
            pass

        return None

    def update_staff_member_with_profile_data(self, staff_member: StaffMember,
                                              profile_data: Dict[str, Any]) -> StaffMember:
        """Update staff member with extracted profile data"""
        staff_member.profile_image_link = profile_data.get('profile_image_link')
        staff_member.bio = profile_data.get('bio', '')
        return staff_member
