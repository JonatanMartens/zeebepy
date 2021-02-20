import logging
from dataclasses import dataclass, field
from typing import List, Optional

from pyzeebe import ExceptionHandler, TaskDecorator, Job

logger = logging.getLogger(__name__)


def default_exception_handler(e: Exception, job: Job) -> None:
    logger.warning(f"Task type: {job.type} - failed job {job}. Error: {e}.")
    job.set_failure_status(f"Failed job. Error: {e}")


@dataclass
class TaskConfig:
    type: str
    exception_handler: ExceptionHandler = default_exception_handler
    timeout: int = 10000
    max_jobs_to_activate: int = 32
    variables_to_fetch: Optional[List[str]] = None
    before: List[TaskDecorator] = field(default_factory=list)
    after: List[TaskDecorator] = field(default_factory=list)