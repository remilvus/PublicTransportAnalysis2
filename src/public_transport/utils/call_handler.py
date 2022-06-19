"""Component implementing the circuit breaker pattern."""
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, Callable, Generic, Optional

T = TypeVar("T")


@dataclass(frozen=True)
class CallResult(Generic[T]):
    """Result of a CallHandler-managed function call.

    Attributes
    ----------
    success : bool
        Indicates whether the call was correctly executed.
    returned_value : Optional[T]
        Contains returned value, if the call was correctly executed.
    wait_until : Optional[datetime]
        If the call wasn't successful, this value indicates when next call is allowed.

    """

    success: bool
    returned_value: Optional[T]
    wait_until: Optional[datetime]


class CallHandler:
    """Function wrapper preventing quick series of failed executions."""

    def __init__(self, break_count: int, break_length: float):
        self.last_success = datetime.now()
        self.failure_count = 0
        self.break_count = break_count
        self.break_length = break_length

    def handle_call(self, func: Callable[[], T]) -> CallResult[T]:
        """Call `func` if internal policy allows it."""
        raise NotImplementedError()
        # todo: remove call_handler fixture from tests when CallHandler is implemented
