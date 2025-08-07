#!/usr/bin/env python3
"""
Staff Directory Crawler - Main Entry Point
A comprehensive web scraping tool for extracting staff information from educational institution directories.
Now includes profile crawling capabilities.

Usage:
    python main.py [--resume] [--verbose] [--limit N] [--profiles] [--no-profiles]

Options:
    --resume        Resume from existing jobs queue
    --verbose       Enable verbose logging and detailed metrics
    --limit         Limit number of schools to process (for testing)
    --profiles      Enable profile crawling (crawl individual staff profile pages)
    --no-profiles   Disable profile crawling (directory pages only)

Environment Variables:
    See config.py for full list of configurable options
"""

import argparse
import asyncio
import sys

from src.staff_crawler import StaffCrawler


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Staff Directory Crawler - Extract staff information from educational directories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                              # Fresh crawl of all enabled schools
    python main.py --resume                     # Resume from existing job queue
    python main.py --verbose --limit 10         # Test run with detailed logging
    python main.py --resume --verbose           # Resume with detailed progress tracking
    python main.py --profiles                   # Crawl directories AND individual profiles
    python main.py --no-profiles                # Only crawl directory pages
    python main.py --resume --profiles          # Resume crawl including profile phase

Configuration:
    Modify config.py or use environment variables to adjust:
    - Concurrency settings (MAX_CONCURRENT_JOBS, REQUEST_DELAY)
    - Profile crawling (ENABLE_PROFILE_CRAWLING, PROFILE_REQUEST_DELAY)
    - Browser timeouts (BROWSER_TIMEOUT, PAGE_TIMEOUT)
    - Processing chunks (ROWS_PER_CHUNK, YIELD_FREQUENCY)
    - File paths (INPUT_FILE, OUTPUT_FILE)
        """
    )

    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume crawling from existing jobs queue (jobs.csv and profile_jobs.csv)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging with detailed metrics and progress tracking'
    )

    parser.add_argument(
        '--limit',
        type=int,
        metavar='N',
        help='Limit number of schools to process (useful for testing)'
    )

    profile_group = parser.add_mutually_exclusive_group()
    profile_group.add_argument(
        '--profiles',
        action='store_true',
        help='Enable profile crawling (crawl individual staff profile pages after directory crawling)'
    )

    profile_group.add_argument(
        '--no-profiles',
        action='store_true',
        help='Disable profile crawling (only crawl directory pages)'
    )

    return parser.parse_args()


async def main():
    """Main entry point for the staff directory crawler"""
    args = parse_arguments()

    print("=" * 60)
    print("Staff Directory Crawler - Educational Institution Data Extraction")
    print("=" * 60)

    if args.resume:
        print("📋 Mode: Resuming from existing job queue")
    else:
        print("🚀 Mode: Fresh crawl")

    if args.verbose:
        print("📊 Logging: Verbose mode enabled")

    if args.limit:
        print(f"🔢 Limit: Processing maximum {args.limit} schools")

    if args.profiles:
        crawl_profiles = True
        print("👤 Profile Crawling: Enabled")
    elif args.no_profiles:
        crawl_profiles = False
        print("👤 Profile Crawling: Disabled")
    else:
        from src.config import ENABLE_PROFILE_CRAWLING
        crawl_profiles = ENABLE_PROFILE_CRAWLING
        print(f"👤 Profile Crawling: {'Enabled' if crawl_profiles else 'Disabled'} (from config)")

    print("-" * 60)

    crawler = StaffCrawler(verbose=args.verbose)

    try:
        await crawler.initialize()

        print("✅ Crawler initialized successfully")
        print("🌐 Starting web scraping process...")

        if crawl_profiles:
            print("📄 Phase 1: Directory crawling")
            print("👤 Phase 2: Profile crawling (if profiles found)")
        else:
            print("📄 Single phase: Directory crawling only")

        print("-" * 60)

        await crawler.crawl(resume=args.resume, limit=args.limit, crawl_profiles=crawl_profiles)

        print("-" * 60)
        print("🎉 Crawl completed successfully!")
        print(f"📊 Total staff members extracted: {len(crawler.all_staff_members)}")

        if crawl_profiles:
            profile_crawled_count = sum(1 for sm in crawler.all_staff_members if sm.profile_crawled)
            print(f"👤 Staff members with profile data: {profile_crawled_count}")

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("⏹️  Crawl interrupted by user")
        print("💾 Progress has been saved automatically")
        print("🔄 Use --resume to continue from where you left off")
        print("=" * 60)
        sys.exit(0)

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Crawler failed with error: {e}")
        print("💾 Partial progress has been saved")
        print("🔍 Check crawler.log for detailed error information")
        print("🔧 Try adjusting configuration in config.py if issues persist")
        print("=" * 60)
        sys.exit(1)


def run_crawler():
    """Wrapper function to run the async main function"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:

        print("\nShutdown requested by user")
        sys.exit(0)
    except Exception as e:
        print(f"Failed to start crawler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_crawler()
