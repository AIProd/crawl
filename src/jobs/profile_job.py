from dataclasses import dataclass

from src.jobs.base_job import BaseJob


@dataclass
class ProfileJob(BaseJob):

    def process(self):
        """Process staff directory job"""
        print("Soon implemented")