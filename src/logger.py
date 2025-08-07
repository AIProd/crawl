"""
Logging utilities for Staff Directory Crawler
Provides centralized logging configuration and progress tracking
"""

import logging
import sys
import time

from src.config import LOG_LEVEL


class Logger:
    """Centralized logging configuration"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

    def setup_logging(self):
        """Configure logging with appropriate handlers and formatters"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        level = logging.DEBUG if self.verbose else getattr(logging, LOG_LEVEL)

        logging.basicConfig(
            level=level,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('crawler.log', mode='a')
            ]
        )

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self.logger


class ProgressTracker:
    """Track and display crawling progress with metrics"""

    def __init__(self, total_jobs: int, verbose: bool = False):
        self.total_jobs = total_jobs
        self.completed = 0
        self.failed = 0
        self.start_time = time.time()
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

    def update_completed(self):
        """Mark a job as completed and log progress"""
        self.completed += 1
        self._log_progress()

    def update_failed(self):
        """Mark a job as failed and log progress"""
        self.failed += 1
        self._log_progress()

    def _log_progress(self):
        """Log current progress with optional detailed metrics"""
        progress = (self.completed + self.failed) / self.total_jobs * 100
        elapsed = time.time() - self.start_time

        if self.verbose:
            rate = (self.completed + self.failed) / elapsed if elapsed > 0 else 0
            eta = (self.total_jobs - self.completed - self.failed) / rate if rate > 0 else 0

            self.logger.info(
                f"Progress: {progress:.1f}% ({self.completed + self.failed}/{self.total_jobs}) | "
                f"Success: {self.completed} | Failed: {self.failed} | "
                f"Rate: {rate:.2f}/s | ETA: {eta:.0f}s"
            )
        else:
            self.logger.info(
                f"Progress: {progress:.1f}% - Completed: {self.completed}, Failed: {self.failed}"
            )
