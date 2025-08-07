"""
BaseJob management for Staff Directory Crawler
Unified job queue with single table and flexible data handling
"""
import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

import polars as pl

from src.config import FAILED_JOBS_FILE, REQUEST_DELAY, MAX_RETRIES
from src.jobs.base_job import BaseJob, JobType, FailedJob


class JobManager:
    """Unified job queue manager with a single jobs table"""

    def __init__(self, logger: logging.Logger, jobs_file: str = 'jobs.csv'):
        self.logger = logger
        self.jobs_file = jobs_file
        self.completed_count = 0
        self.jobs: List[BaseJob] = []

    def create_jobs_from_input(self, input_file: str, limit: Optional[int] = None):
        """Create directory jobs from input CSV file"""
        if not Path(input_file).exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        schools_df = self._read_schools_dataframe(input_file)

        if limit:
            schools_df = schools_df.limit(limit)

        self.jobs = self._create_directory_jobs_from_dataframe(schools_df)
        self.logger.info(f"Created {len(self.jobs)} directory jobs from input file")

    def get_jobs_by_type(self, job_type: JobType) -> List[BaseJob]:
        """
        Filters self.jobs to return only jobs of a specific type.
        """
        filtered_jobs = [job for job in self.jobs if job.type == job_type.value]
        return filtered_jobs

    def _read_schools_dataframe(self, input_file: str) -> pl.DataFrame:
        """Read schools dataframe with proper schema"""
        return pl.read_csv(input_file, infer_schema_length=10000).select(
            pl.col('school_id').alias('id'),
            pl.col('school_name').alias('name'),
            pl.col('url'),
            pl.col('is_enabled').eq('1'),
        ).filter(
            pl.col('url').is_not_null(),
            pl.col('is_enabled').eq(True),
            # pl.col('url').eq('https://athletics.hagerstowncc.edu/athletics/directory/index') # TODO: For development purposes remove on prod
        )

    def _read_schools_dataframe_fallback(self, input_file: str) -> pl.DataFrame:
        """Fallback method for reading schools dataframe"""
        return pl.read_csv(input_file).select(
            pl.col('school_id').alias('id'),
            pl.col('school_name').alias('name'),
            pl.col('url')
        ).filter(
            pl.col('url').is_not_null()
        )

    def _create_directory_jobs_from_dataframe(self, schools_df: pl.DataFrame) -> List[BaseJob]:
        """Create directory BaseJob objects from dataframe rows"""
        jobs = []
        for row in schools_df.iter_rows(named=True):
            job = BaseJob(type=JobType.DIRECTORY.value)

            job.data = row

            jobs.append(job)
        return jobs

    def save_jobs(self):
        """Save jobs to a unified CSV file"""
        if not self.jobs:
            Path(self.jobs_file).touch()
            return

        jobs_data = [job.to_dict() for job in self.jobs]
        df = pl.DataFrame(jobs_data)
        df.write_csv(self.jobs_file)
        self.logger.info(f"Saved {len(self.jobs)} jobs to {self.jobs_file}")

    def load_jobs(self, job_type: Optional[JobType] = None):
        """Load jobs from unified CSV, optionally filtered by job type"""
        if not Path(self.jobs_file).exists():
            return []

        try:
            jobs_df = pl.read_csv(self.jobs_file)

            if jobs_df.height == 0:
                return []

            if job_type is not None:
                jobs_df = jobs_df.filter(pl.col('job_type') == job_type.value)

            jobs = self._create_jobs_from_csv_data(jobs_df)
            job_type_str = f" {job_type.value}" if job_type else ""

            self.logger.info(f"Loaded {len(jobs)}{job_type_str} jobs from {self.jobs_file}")
            self.jobs = jobs

        except Exception as e:
            self.logger.error(f"Error loading jobs: {e}")

    def _create_jobs_from_csv_data(self, jobs_df: pl.DataFrame) -> List[BaseJob]:
        """Create BaseJob objects from CSV data"""
        jobs = []
        for row in jobs_df.iter_rows(named=True):
            try:
                job = BaseJob.from_dict(row)
                jobs.append(job)
            except Exception as e:
                self.logger.warning(f"Error creating job from row: {e}")
                continue
        return jobs

    def save_failed_job(self, job: BaseJob, error_message: str):
        """Save failed job to failed jobs CSV"""

        failed_job = FailedJob(
            job_uuid=job.uuid,
            error_message=error_message,
            job_class=job.__class__.__name__,
            job=json.dumps(job.to_dict(), default=str),
        )

        failed_jobs = self._load_existing_failed_jobs()
        failed_jobs = self._update_or_add_failed_job(failed_jobs, failed_job)
        self._save_failed_jobs_to_csv(failed_jobs)

        job_data = job.data
        job_name = job_data['name']

        self.logger.warning(f"BaseJob {job_name} failed (attempt {job.retry_count}): {error_message[:100]}...")

    def _load_existing_failed_jobs(self) -> List[FailedJob]:
        """Load existing failed jobs from CSV"""
        failed_jobs = []
        if Path(FAILED_JOBS_FILE).exists():
            try:
                failed_df = pl.read_csv(FAILED_JOBS_FILE, schema=self._get_failed_job_schema())
                failed_jobs = self._create_jobs_from_csv_data(failed_df)
            except Exception as e:
                self.logger.warning(f"Error loading existing failed jobs: {e}")
        return failed_jobs

    def _update_or_add_failed_job(self, failed_jobs: List[FailedJob], job: FailedJob) -> List[FailedJob]:
        """Update existing failed job or add new one"""
        existing_job_index = None
        for i, existing_job in enumerate(failed_jobs):
            if existing_job.job_uuid == job.job_uuid:
                existing_job_index = i
                break

        if existing_job_index is not None:
            failed_jobs[existing_job_index] = job
        else:
            failed_jobs.append(job)

        return failed_jobs

    def _save_failed_jobs_to_csv(self, failed_jobs: List[FailedJob]):
        """Save failed jobs list to CSV"""
        if not failed_jobs:
            Path(FAILED_JOBS_FILE).touch()
            return

        failed_jobs_data = [asdict(job) for job in failed_jobs]
        df = pl.DataFrame(failed_jobs_data, schema=self._get_failed_job_schema())
        df.write_csv(FAILED_JOBS_FILE)

    def _get_failed_job_schema(self) -> dict:
        """Get the schema definition for unified job CSV files"""
        return {
            'job_uuid': pl.Utf8,
            'error_message': pl.Utf8,
            'job_class': pl.Utf8,
            'job': pl.Utf8,
            'created_at': pl.Utf8,
        }

    def complete_job(self, job: BaseJob):
        """Mark the job as completed"""
        self.jobs.remove(job)
        self.save_jobs()

    def flush_jobs(self):
        """Remove job files for a fresh start"""
        if Path(self.jobs_file).exists():
            Path(self.jobs_file).unlink()
            self.logger.info(f"Removed scheduled jobs from {self.jobs_file}")
            return

    def get_job_counts_by_type(self) -> dict:
        """Get counts of jobs by type"""
        jobs = self.load_jobs()
        counts = {job_type: 0 for job_type in JobType}

        for job in jobs:
            counts[job.job_type] += 1

        return {job_type.value: count for job_type, count in counts.items()}

    def attempt_job_reschedule(self, job: BaseJob, error_message: str):
        self.jobs.remove(job)
        job.retry_count += 1

        if job.retry_count > MAX_RETRIES:
            self.logger.warning(f"Job {job.uuid} exceeded retry count.")
            self.save_failed_job(job, error_message)
            return

        job.retry_delay = (2 ** job.retry_count) * REQUEST_DELAY
        self.jobs.append(job)
        self.save_jobs()
