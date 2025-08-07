import asyncio
from typing import List

from playwright.async_api import Page

from src.config import PAGE_TIMEOUT
from src.models import StaffMember
from src.sites.site import Site
from src.utils import normalize_headers_auto, make_full_url, clean_cell_text


class ToggleViewSite(Site):
    async def validate_type(self, page: Page):
        table_locator = page.locator("table")
        table_count = await table_locator.count()

        if table_count == 0:
            raise Exception("No tables found")

        if table_count < 2:
            raise Exception("Wrong site type detected - less than 2 tables found")

        # Heading indicates department
        department_row_locator = page.locator(".s-table-header__row.s-table-header__row--heading")
        department_row_count = await department_row_locator.count()

        if department_row_count == 0:
            raise Exception("Wrong site type detected - no department row found")

        if department_row_count < table_count:
            raise Exception("Department count does not match table count")


    async def process(self, page: Page) -> List[StaffMember]:
        switch_to_table_view_button = page.locator("[id*='_viewType_table']")
        await switch_to_table_view_button.click()

        await asyncio.wait_for(
            page.wait_for_selector(".s-table-header__row.s-table-header__row--heading"),
            timeout=PAGE_TIMEOUT / 1000
        )

        await self.validate_type(page)
        url = page.url

        tables_locator = page.locator("table")
        tables_count = await tables_locator.count()

        staff_members = []
        for table_index in range(tables_count):
            table_locator = tables_locator.nth(table_index)
            department_locator = table_locator.locator(".s-table-header__row.s-table-header__row--heading")
            header_cells_locator = table_locator.locator(".s-table-header__row.s-table-header__row--subheading > th")
            department_text = (await department_locator.text_content()).strip()

            headers = []
            for header_cell_index in range(await header_cells_locator.count()):
                header_cell_locator = header_cells_locator.nth(header_cell_index)
                headers.append(
                    (await header_cell_locator.text_content()).strip()
                )

            normalized_headers = normalize_headers_auto(headers)

            rows_locator = table_locator.locator('tbody >  tr')
            rows_count = await rows_locator.count()

            if rows_count == 0:
                continue

            for row_index in range(rows_count):
                row_locator = rows_locator.nth(row_index)
                cells_locator = row_locator.locator('td')
                cells_count = await cells_locator.count()


                cells = []
                for cell_index in range(cells_count):
                    cell_locator = cells_locator.nth(cell_index)
                    link_locator = cell_locator.locator('a')

                    cell_url = None
                    if await link_locator.count() > 0:
                        cell_url = await link_locator.first.get_attribute('href')

                    cells.append({
                        'value': clean_cell_text((await cell_locator.text_content()).strip()),
                        'url': make_full_url(cell_url, url) if cell_url else None,
                    })

                row_dict = dict(zip(normalized_headers, cells))

                if not row_dict:
                    continue

                staff_members.append(
                    StaffMember(
                        name=row_dict.get('name', {}).get('value', ''),
                        title=row_dict.get('title', {}).get('value', ''),
                        email=row_dict.get('email', {}).get('value', ''),
                        phone=row_dict.get('phone', {}).get('value', ''),
                        department=department_text,
                        profile_link=row_dict.get('name', {}).get('url', ''),
                        school_name=self.data.get('name', ''),
                        school_url=self.data.get('url', ''),
                        school_id=self.data.get('id', None),
                    )
                )

        return staff_members