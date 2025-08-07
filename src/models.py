"""
Data models for Staff Directory Crawler
Unified job system with single table and flexible data column
"""
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class CrawledTable:
    """Represents a table extracted from a webpage"""
    headers: List[str]
    rows: List[Dict[str, str]]
    links: List[Dict[str, str]] = None
    department: Optional[str] = None


@dataclass
class StaffMember:
    """Represents a staff member with all their information"""
    name: str
    title: Optional[str] = ''
    department: Optional[str] = ''
    email: Optional[str] = ''
    phone: Optional[str] = ''
    twitter: Optional[str] = ''
    discord: Optional[str] = ''
    sport: Optional[str] = ''
    school_name: Optional[str] = ''
    school_url: Optional[str] = ''
    school_id: Optional[int] = ''
    profile_link: Optional[str] = ''
    profile_image_link: Optional[str] = ''
    bio: Optional[str] = ''

    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

