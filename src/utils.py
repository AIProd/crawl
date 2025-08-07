import asyncio
import re
from difflib import SequenceMatcher
from typing import List
from urllib.parse import urlparse

from playwright.async_api import Page

from src.config import BROWSER_TIMEOUT
from src.sites.site import Site


async def _load_page(page: Page, url: str):
    """Load the initial page with error handling"""
    try:
        response = await asyncio.wait_for(
            page.goto(url, timeout=BROWSER_TIMEOUT, wait_until='domcontentloaded'),
            timeout=BROWSER_TIMEOUT / 1000
        )
        if response.status != 200:
            raise Exception(f"HTTP {response.status}")
    except asyncio.TimeoutError:
        raise Exception("Timeout loading page")
    except Exception as e:
        raise Exception(f"Failed to load page: {str(e)}")


async def detect_site_type(page: Page, data: dict) -> Site | None:

    is_toggle_view_site = await page.locator("[id*='_viewType_table']").count() > 0
    is_single_table_department_as_row = await page.locator(".sidearm-table").count() == 1
    is_multi_table_section_department_above_table_site = await page.locator('section[class="staff-directory"]').count() > 0
    is_single_table_title_under_name_no_department_site = await page.locator("table[class='roster']").count() == 1


    if is_toggle_view_site:
        from src.sites.toggle_view_site import ToggleViewSite
        return ToggleViewSite(data)

    if is_single_table_department_as_row:
        from src.sites.single_table_department_as_row import SingleTableDepartmentAsRow
        return SingleTableDepartmentAsRow(data)

    if is_multi_table_section_department_above_table_site:
        from src.sites.multi_table_sections_department_above_table import MultiTableSectionsAboveTable
        return MultiTableSectionsAboveTable(data)

    if is_single_table_title_under_name_no_department_site:
        from src.sites.single_table_title_under_name_no_department import SingleTableTitleUnderNameNoDepartment
        return SingleTableTitleUnderNameNoDepartment(data)

    return None


def normalize_headers_auto(headers: List[str], disable_default: bool = False) -> List[str]:
    """Automatically normalize headers using pattern recognition and fuzzy matching"""
    default_headers = ['name', 'title', 'email', 'phone']

    if not disable_default and (not headers or not any(h and h.strip() for h in headers)):
        return default_headers.copy()

    patterns = {
        'name': {
            'keywords': ['name', 'full_name', 'fullname'],
            'patterns': [r'\bname\b', r'\bfull.*name\b', r'\bfullname\b'],
            'result': 'name'
        },
        'email_address': {
            'keywords': ['email', 'mail', 'address'],
            'patterns': [r'\bemail\b', r'\bmail\b', r'\bemail.*addr\b'],
            'result': 'email'
        },
        'phone': {
            'keywords': ['phone', 'tel', 'telephone', 'mobile', 'cell'],
            'patterns': [r'\b(phone|tel|telephone|mobile|cell)\b'],
            'result': 'phone'
        },
        'title': {
            'keywords': ['position', 'job', 'role'],
            'patterns': [r'\b(job|position|role).*title\b', r'^title$'],
            'result': 'title'
        }
    }

    def similarity(a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def clean_header(header):
        cleaned = re.sub(r'[^\w\s]', ' ', header.lower())
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def match_header(header):
        if not header or not header.strip():
            return 'empty_column'

        if '@' in header:
            return header.lower().replace(' ', '_')

        cleaned = clean_header(header)
        best_match = None
        best_score = 0

        for category, config in patterns.items():
            score = 0

            for keyword in config['keywords']:
                keyword_pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(keyword_pattern, cleaned):
                    score += 1.0
                else:
                    for word in cleaned.split():
                        sim = similarity(word, keyword)
                        if sim > 0.8:
                            score += sim * 0.8

            for pattern in config['patterns']:
                if re.search(pattern, cleaned):
                    score += 0.7

            if score > 1:
                score *= 1.2

            if score > best_score:
                best_score = score
                best_match = config['result']

        if best_score < 0.5:
            generic = re.sub(r'[^\w\s]', '', header.lower())
            generic = re.sub(r'\s+', '_', generic)
            generic = re.sub(r'_+', '_', generic).strip('_')
            return generic if generic else f'column_{headers.index(header)}'

        return best_match

    normalized_headers = []
    used_names = {}

    for i, header in enumerate(headers):
        normalized = match_header(header)

        if normalized in used_names:
            used_names[normalized] += 1
            normalized = f"{normalized}_{used_names[normalized]}"
        else:
            used_names[normalized] = 0

        normalized_headers.append(normalized)

    return normalized_headers


def is_internal_url(url: str, base_domain: str) -> bool:
    """Check if URL is internal to the base domain"""
    if not url:
        return False

    if url.startswith('/') or not url.startswith('http'):
        return True

    parsed_url = urlparse(url)
    parsed_base = urlparse(base_domain)

    return parsed_url.netloc == parsed_base.netloc

def make_full_url(url: str, base_url: str) -> str:
    """Convert path to full URL if needed"""
    if not url:
        return url

    if url.startswith('http'):
        return url

    if url.startswith('/'):
        return base_url.rstrip('/') + url
    else:
        return base_url.rstrip('/') + '/' + url

def clean_cell_text(raw_text: str) -> str:
    """Generic function to clean any messy cell content"""
    if not raw_text:
        return ""

    clean_text = ' '.join(raw_text.split())

    email_match = re.match(r'[\w.-]+@[\w.-]+\.\w+', clean_text)
    if email_match:
        return email_match.group()

    phone_match = re.match(r'[\d\-()\s]{10,}', clean_text)
    if phone_match and not email_match:
        return phone_match.group().strip()

    url_match = re.search(r'https?://[\w.-]+', clean_text)
    if url_match and not email_match:
        return url_match.group()

    js_keywords = ['var ', 'function', 'document.', 'getElementById', 'innerHTML', 'innerText']
    if any(keyword in clean_text for keyword in js_keywords):
        lines = raw_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not any(keyword in line for keyword in js_keywords):
                return line

    return clean_text