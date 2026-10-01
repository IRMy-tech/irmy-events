from typing import Any, Literal, Optional
from pydantic import BaseModel


class SchedulerSendEvent(BaseModel):
    routingKey: str
    eventData: dict[str, Any]


class SchedulerRequestCreate(BaseModel):
    """scheduler.request — action=create, scheduleType=oneShot.
    Used for escalation timers: executeAt is a UNIX timestamp."""

    internalScheduleId: str
    action: Literal["create"]
    description: Optional[str] = None
    scheduleType: Literal["oneShot"]
    executeAt: int
    sendEvent: SchedulerSendEvent


class SchedulerRequestCreateRecurring(BaseModel):
    """scheduler.request — action=create, scheduleType=recurring.
    Used for on-call rotation extend: executeWhen is a cron string."""

    internalScheduleId: str
    action: Literal["create"]
    description: Optional[str] = None
    scheduleType: Literal["recurring"]
    executeWhen: str
    sendEvent: SchedulerSendEvent


class SchedulerRequestCancel(BaseModel):
    """scheduler.request — action=cancel.
    Cancels a previously scheduled one-shot or recurring job."""

    internalScheduleId: str
    action: Literal["cancel"]
    scheduleType: Literal["oneShot", "recurring"]
