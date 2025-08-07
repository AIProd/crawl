from typing import List

from playwright.async_api import Page

from src.models import StaffMember
from src.sites.site import Site
from src.utils import normalize_headers_auto, clean_cell_text, make_full_url


class MultiTableSectionsAboveTable(Site):
    async def validate_type(self, page: Page):
        table_locator = page.locator("table")
        table_count = await table_locator.count()

        if table_count == 0:
            raise Exception("No tables found")

        if table_count < 2:
            raise Exception("Wrong site type detected - less than 2 tables found")

        department_row_locator = page.locator(
            "section[class=staff-directory] > h1, section[class=staff-directory] > h2, section[class=staff-directory] > h3, section[class=staff-directory] > h4, section[class=staff-directory] > h5, section[class=staff-directory] > h6")
        department_row_count = await department_row_locator.count()

        if department_row_count == 0:
            raise Exception("Wrong site type detected - no department section found")


    async def process(self, page: Page) -> List[StaffMember]:
        await self.validate_type(page)
        url = page.url

        sections_locator = page.locator("section[class='staff-directory']")
        sections_count = await sections_locator.count()

        staff_members = []
        for section_index in range(sections_count):
            section_locator = sections_locator.nth(section_index)
            table_locator = section_locator.locator("table")

            department_locator = section_locator.locator("h1, h2, h3, h4, h5, h6")
            department_text = ''
            if await department_locator.count() > 0:
                department_text = (await department_locator.text_content()).strip()

            header_cells_locator = table_locator.locator("th")

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