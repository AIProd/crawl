"""
Main crawler orchestrator for Staff Directory Crawler
Coordinates all components and manages the crawling process with unified job system
"""

import asyncio
import gc
from dataclasses import asdict
from typing import List, Optional

import polars as pl

from src.browser_pool import BrowserPool
from src.config import (
    MAX_CONCURRENT_JOBS, REQUEST_DELAY, MAX_RETRIES,
    PAGE_TIMEOUT, BATCH_SAVE_SIZE, OUTPUT_FILE, INPUT_FILE, ENABLE_PROFILE_CRAWLING, PROFILE_REQUEST_DELAY,
    MAX_PROFILE_CONCURRENT_JOBS, JOBS_FILE, JOB_TIMEOUT
)
from src.job_manager import JobManager
from src.jobs.base_job import JobType, BaseJob
from src.jobs.staff_directory_job import StaffDirectoryJob
from src.logger import Logger, ProgressTracker
from src.models import StaffMember
from src.profile_extractor import ProfileExtractor


class StaffCrawler:
    """Main crawler orchestrator with unified job system"""

    def __init__(self, verbose: bool = False):
        self.logger_manager = Logger(verbose)
        self.logger = self.logger_manager.get_logger()
        self.job_manager = JobManager(self.logger, JOBS_FILE)
        self.pending_jobs = []
        self.profile_extractor = ProfileExtractor(self.logger)
        self.browser_pool: Optional[BrowserPool] = None
        self.progress_tracker: Optional[ProgressTracker] = None
        self.all_staff_members: List[StaffMember] = []
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_JOBS)
        self.profile_semaphore = asyncio.Semaphore(MAX_PROFILE_CONCURRENT_JOBS)
        self.verbose = verbose

    async def initialize(self):
        """Initialize crawler resources"""
        self.browser_pool = BrowserPool(pool_size=min(MAX_CONCURRENT_JOBS + MAX_PROFILE_CONCURRENT_JOBS, 4))
        await self.browser_pool.initialize()
        self.logger.info("Crawler initialized successfully")

    async def crawl(self, resume: bool = False, limit: Optional[int] = None, crawl_profiles: bool = None):
        """Main crawling method with optional profile crawling"""

        if crawl_profiles is None:
            crawl_profiles = ENABLE_PROFILE_CRAWLING

        try:
            # Phase 1: Directory crawling
            await self._prepare_directory_jobs(resume, limit)

            await self._setup_crawl_session(JobType.DIRECTORY)
            await self._process_all_jobs(JobType.DIRECTORY)
            await self.save_progress()

            # Phase 2: Profile crawling (if enabled)
            # if crawl_profiles and self.all_staff_members:
            #     self.logger.info("Starting profile crawling phase...")
            #     profile_jobs = await self._prepare_profile_jobs()
            #     if profile_jobs:
            #         await self._setup_crawl_session(profile_jobs, "profile")
            #         await self._process_all_jobs(profile_jobs, JobType.PROFILE)
            #
            # await self._finalize_crawl()

        except KeyboardInterrupt:
            self.logger.info("Crawl interrupted by user")
            # await self.save_progress()
            raise
        except Exception as e:
            self.logger.error(f"Crawl failed: {str(e)}")
            # await self.save_progress()
            raise
        finally:
            if self.browser_pool:
                await self.browser_pool.close_all()

    async def _prepare_directory_jobs(self, resume: bool, limit: Optional[int]):
        """Prepare directory jobs for processing"""
        if resume:
            self.job_manager.load_jobs(JobType.DIRECTORY)
            if not self.job_manager.jobs:
                self.logger.warning("No existing directory jobs found for resume mode")
        else:
            self.job_manager.flush_jobs()
            self.job_manager.create_jobs_from_input(INPUT_FILE, limit)
            self.job_manager.save_jobs()

    async def _setup_crawl_session(self, phase: JobType):
        """Setup progress tracking and logging for a crawl session"""
        num_of_jobs = len(self.job_manager.get_jobs_by_type(phase))
        self.progress_tracker = ProgressTracker(num_of_jobs, self.verbose)
        self.logger.info(f"Starting {phase.value} crawl phase with {num_of_jobs} jobs")

        if phase.value == "directory":
            self.logger.info(f"Max concurrent: {MAX_CONCURRENT_JOBS}, delay: {REQUEST_DELAY}s")
        else:
            self.logger.info(f"Max concurrent: {MAX_PROFILE_CONCURRENT_JOBS}, delay: {PROFILE_REQUEST_DELAY}s")

    async def _process_all_jobs(self, job_type: JobType):
        """Process all jobs using batch processing"""
        batch_number = 1

        num_of_jobs = len(self.job_manager.get_jobs_by_type(job_type))

        if job_type == JobType.PROFILE.value:
            batch_size = min(BATCH_SAVE_SIZE, MAX_PROFILE_CONCURRENT_JOBS, num_of_jobs)
        else:
            batch_size = min(BATCH_SAVE_SIZE, MAX_CONCURRENT_JOBS, num_of_jobs)

        while self.job_manager.get_jobs_by_type(job_type):
            batch = self.job_manager.jobs[:batch_size]
            await self._process_batch(batch, job_type)
            await self.save_progress()

            self.logger.info(
                f"Batch {batch_number} completed"
            )

            gc.collect()
            if self.job_manager.jobs:
                self.logger.info(f"Batch {batch_number} completed, pausing before next batch...")
                await asyncio.sleep(5.0)

            batch_number += 1

    async def _process_batch(self, batch: List[BaseJob], job_type: JobType):
        """Process a single batch of jobs"""
        tasks = [self.process_directory_job(job) for job in batch]
        timeout_multiplier = MAX_RETRIES

        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=len(batch) * PAGE_TIMEOUT * timeout_multiplier / 1000
            )
        except asyncio.TimeoutError:
            err_msg = f"{job_type.value.title()} batch processing timeout"
            self.logger.error(err_msg)
            for job in batch:
                self.job_manager.attempt_job_reschedule(job, err_msg)

    async def _finalize_crawl(self):
        """Finalize crawl session"""
        await self.save_progress()

        self.logger.info("All jobs completed successfully - cleaned up job queue")
        self.job_manager.flush_jobs()

        self.logger.info(f"Crawl completed. Total staff members: {len(self.all_staff_members)}")

    async def process_directory_job(self, job: StaffDirectoryJob) -> bool:
        """Process a single directory job"""
        job_data = job.data

        page = None

        await asyncio.sleep(job.retry_delay)

        self.logger.debug(f"Semaphore state before acquire: {getattr(self.semaphore, '_value', 'unknown')}")
        async with self.semaphore:
            try:
                # Jittered delay to prevent thundering herd
                jitter = REQUEST_DELAY * (0.5 + (hash(job_data['url']) % 100) / 200.0)
                await asyncio.sleep(jitter)

                page = await self.browser_pool.get_page()
                self.logger.info(f"Started processing directory {job_data['name']} (ID: {job.uuid})")

                if page.is_closed():
                    raise Exception("Page was closed before processing could begin")

                staff_directory_job = StaffDirectoryJob.from_base_job(job)

                ### TODO: Step 1) Identify table type, Step 2) Switch view / dynamic load if applicable, Step 3) Crawl page, Step 4) Create Staff Member with crawled data
                staff_members = await asyncio.wait_for(
                    staff_directory_job.process(page),
                    timeout=JOB_TIMEOUT
                )

                if staff_members:
                    self.all_staff_members.extend(staff_members)
                    self.job_manager.complete_job(job)
                    self.progress_tracker.update_completed()

                    self.logger.info(
                        f"Successfully processed {job_data['name']}: {len(staff_members)} staff members extracted"
                    )
                    return True
                else:
                    raise Exception("No staff members extracted")

            except asyncio.TimeoutError:
                await self._handle_job_timeout(job)
                return False
            except Exception as e:
                await self._handle_job_error(job, e)
                return False
            finally:
                if page:
                    await self.browser_pool.close_page_safely(page)

    async def _handle_job_timeout(self, job: BaseJob):
        """Handle job timeout with retry logic"""
        error_msg = f"BaseJob timeout after {PAGE_TIMEOUT / 1000}s"
        self.logger.error(f"Job {job.data['name']} timed out: {error_msg}")
        self.job_manager.attempt_job_reschedule(job, error_msg)

    async def _handle_job_error(self, job: BaseJob, error: Exception):
        """Handle job error with retry logic"""
        error_msg = str(error)
        self.logger.error(f"Error processing {job.data['name']}: {error_msg}")

        if "closed" in error_msg.lower() or "target" in error_msg.lower():
            self.logger.error(f"Page closure detected for {job.data['name']}, marking as failed without retry")
            self.job_manager.save_failed_job(job, error_msg)
            self.progress_tracker.update_failed()
        else:
            self.job_manager.attempt_job_reschedule(job, error_msg)

    async def save_progress(self):
        """Save current progress to CSV"""
        if not self.all_staff_members:
            return

        try:
            staff_data = [asdict(member) for member in self.all_staff_members]
            df = pl.DataFrame(staff_data)
            df.write_csv(OUTPUT_FILE)
            self.logger.info(f"Saved {len(self.all_staff_members)} staff members to {OUTPUT_FILE}")
        except Exception as e:
            self.logger.error(f"Error saving progress: {e}")
            await self._save_progress_with_none_handling()

    async def _save_progress_with_none_handling(self):
        """Save progress with explicit None value handling"""
        try:
            staff_data = []
            for member in self.all_staff_members:
                data = asdict(member)
                for key, value in data.items():
                    if value is None:
                        data[key] = "" if key != "school_id" else 0
                staff_data.append(data)

            df = pl.DataFrame(staff_data)
            df.write_csv(OUTPUT_FILE)
            self.logger.info(
                f"Saved {len(self.all_staff_members)} staff members to {OUTPUT_FILE} (with None handling)"
            )
        except Exception as e2:
            self.logger.error(f"Failed to save progress even with None handling: {e2}")
            raise e2
