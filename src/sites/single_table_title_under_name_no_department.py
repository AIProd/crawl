from playwright.async_api import Page

from src.models import StaffMember
from src.sites.site import Site
from src.utils import normalize_headers_auto, make_full_url, clean_cell_text


class SingleTableTitleUnderNameNoDepartment(Site):

    async def validate_type(self, page: Page):
        table_locator = page.locator("table[class='roster']")
        table_count = await table_locator.count()

        if table_count == 0:
            raise Exception("No tables found")

        if table_count > 1:
            raise Exception("Wrong site type detected - multiple tables found")


    async def process(self, page: Page):
        await self.validate_type(page)

        table_locator = page.locator("table").first


        header_cells_locator = table_locator.locator(".roster-header > td")
        headers = []
        for header_cell_index in range(await header_cells_locator.count()):
            header_cell_locator = header_cells_locator.nth(header_cell_index)
            headers.extend(
                (await header_cell_locator.text_content()).strip().split('&')
            )

        normalized_headers = normalize_headers_auto(headers)

        rows_locator = page.locator("tr[class*='roster-row']")
        rows_count = await rows_locator.count()
        staff_members = []

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

                cell_texts = (await cell_locator.text_content()).strip().split('\n')

                for cell_text in cell_texts:
                    cells.append({
                        'value': clean_cell_text(cell_text.strip()),
                        'url': make_full_url(cell_url, page.url) if cell_url else None,
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
                    department='',
                    profile_link=row_dict.get('name', {}).get('url', ''),
                    school_name=self.data.get('name', ''),
                    school_url=self.data.get('url', ''),
                    school_id=self.data.get('id', None),
                )
            )


        return staff_members

