from playwright.async_api import Page

from src.models import StaffMember
from src.sites.site import Site
from src.utils import normalize_headers_auto, make_full_url, clean_cell_text


class SingleTableDepartmentAsRow(Site):

    async def validate_type(self, page: Page):
        table_locator = page.locator("table[class*='sidearm-table']")
        table_count = await table_locator.count()

        if table_count == 0:
            raise Exception("No tables found")

        if table_count > 1:
            raise Exception("Wrong site type detected - multiple tables found")

        department_row_locator = page.locator(".sidearm-staff-category")
        department_row_count = await department_row_locator.count()
        if department_row_count == 0:
            raise Exception("Wrong site type detected - no department row found")


    async def process(self, page: Page):
        await self.validate_type(page)

        table_locator = page.locator("table").first


        header_cells_locator = table_locator.locator("th")
        headers = []
        for header_cell_index in range(await header_cells_locator.count()):
            header_cell_locator = header_cells_locator.nth(header_cell_index)
            headers.append(
                (await header_cell_locator.text_content()).strip()
            )

        normalized_headers = normalize_headers_auto(headers)

        all_rows = await page.locator("tbody > tr").all()
        groups = []
        current_group = []
        for row in all_rows:
            row_class = await row.get_attribute("class")

            if not row_class:
                continue

            if "sidearm-staff-category" in row_class or "":
                if current_group:
                    groups.append(current_group)

                current_group = [row]
            elif "sidearm-staff-member" in row_class or "":
                current_group.append(row)

        if current_group:
            groups.append(current_group)

        staff_members = []
        for group in groups:
            department_locator = group[0]
            rows_locator = group[1:]

            department_text = (await department_locator.text_content()).strip()

            for row_locator in rows_locator:
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
                        department=department_text,
                        profile_link=row_dict.get('name', {}).get('url', ''),
                        school_name=self.data.get('name', ''),
                        school_url=self.data.get('url', ''),
                        school_id=self.data.get('id', None),
                    )
                )


        return staff_members

