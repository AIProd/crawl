import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Literal


class JobType(Enum):
    DIRECTORY = "directory"
    PROFILE = "profile"

@dataclass
class FailedJob:
    job_uuid: str
    error_message: str
    job_class: str
    job: str
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class BaseJob:
    type: str = Literal[JobType.DIRECTORY, JobType.PROFILE]
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    _data_json: str = ""
    _parsed_data: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    retry_delay: int = 0
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        try:
            if self._data_json != '':
                json.loads(self._data_json)
        except json.JSONDecodeError:
            raise ValueError("Initial _data_json is not a valid JSON string.")

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            uuid=data.get('uuid', ''),
            type=data.get('type', ''),
            _data_json=data.get('data', ''),
            retry_count=data.get('retry_count', 0),
            retry_delay=data.get('retry_delay', 0),
            created_at=data.get('created_at', None),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'uuid': self.uuid,
            'type': self.type,
            'data': self._data_json,
            'retry_count': self.retry_count,
            'retry_delay': self.retry_delay,
            'created_at': self.created_at,
        }

    @property
    def data(self) -> Dict[str, Any]:
        """
        Getter for the 'data' field.
        Parses the internal JSON string (_data_json) into a Python dictionary.
        """
        if self._parsed_data is None:
            try:
                self._parsed_data = json.loads(self._data_json)
            except json.JSONDecodeError:
                self._parsed_data = {}

        return self._parsed_data

    @data.setter
    def data(self, value: Dict[str, Any]):
        """
        Setter for the 'data' field.
        Converts a Python dictionary into a JSON string and stores it internally.
        """
        if not isinstance(value, dict):
            raise TypeError("Value for 'data' must be a dictionary.")
        self._data_json = json.dumps(value)

    async def process(self, page):
        pass

    @classmethod
    def from_base_job(cls, base_job):
        pass
