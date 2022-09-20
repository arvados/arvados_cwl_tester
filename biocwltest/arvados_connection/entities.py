import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class Base:

    @classmethod
    def from_dict(cls, **data):
        return cls(**{key: val for key, val in data.items() if key in cls.__dataclass_fields__})


@dataclass
class Project(Base):
    uuid: str
    name: str
    owner_uuid: str
    properties: Dict
    modified_at: datetime
    created_at: datetime
    delete_at: datetime


@dataclass
class Container(Base):
    uuid: str
    owner_uuid: str
    created_at: datetime
    modified_at: datetime
    command: List
    container_image: str
    exit_code: int
    finished_at: datetime
    log: str
    output: str
    runtime_status: Dict
    started_at: datetime
    state: str


class ProcessStatus(enum.Enum):
    COMPLETED = "Completed"
    FAILED = "Failed"
    RUNNING = "Running"
    CANCELLED = "Cancelled"
    QUEUED = "Queued"


@dataclass
class Process(Base):
    def __post_init__(self):
        if self.container.state == "Complete" and self.container.exit_code == 0:
            self.status = ProcessStatus.COMPLETED
        elif self.container.state == "Complete" and self.container.exit_code != 0:
            self.status = ProcessStatus.FAILED
        elif self.container.state == "Cancelled":
            self.status = ProcessStatus.CANCELLED
        elif self.container.state == "Queued":
            self.status = ProcessStatus.QUEUED
        elif self.container.state == "Running":
            self.status = ProcessStatus.RUNNING

    uuid: str
    command: List[str]
    container_count: int
    container_count_max: int
    container_image: str
    container_uuid: str
    created_at: datetime
    log_uuid: str
    modified_at: str
    name: str
    output_name: str
    output_path: str
    output_properties: Dict
    output_ttl: int
    output_uuid: str
    owner_uuid: str
    properties: Dict
    requesting_container_uuid: str
    state: str
    use_existing: bool
    container: Container
    status: ProcessStatus = None


@dataclass
class Collection(Base):
    uuid: str
    name: str
    owner_uuid: str
    properties: Dict
    modified_at: datetime
    created_at: datetime
    delete_at: datetime
    trash_at: datetime
    portable_data_hash: str
    version: int
    manifest_text: str
    file_count: int
    file_size_total: int
