from dataclasses import dataclass, fields
from typing import List

from src.jobs.base_job import BaseJob
from src.models import StaffMember
from src.utils import _load_page, detect_site_type


@dataclass
class StaffDirectoryJob(BaseJob):

    async def process(self, page) -> List[StaffMember]:
        """Process staff directory job"""

        await _load_page(
            page=page,
            url=self.data['url']
        )

        detected_site_type = await detect_site_type(page, self.data)

        if not detected_site_type:
            raise Exception("Failed to detect site type")

        return await detected_site_type.process(page)

    @classmethod
    def from_base_job(cls, base_job: BaseJob):
        base_fields = {f.name: getattr(base_job, f.name)
                       for f in fields(base_job)}

        return cls(**base_fields)
