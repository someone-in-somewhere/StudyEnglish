"""
Timezone utilities for consistent GMT+7 (Vietnam) time handling.
"""

from datetime import datetime, timezone, timedelta

# GMT+7 timezone
GMT7 = timezone(timedelta(hours=7))


def now_gmt7() -> datetime:
    """Get current datetime in GMT+7."""
    return datetime.now(GMT7)


def to_gmt7(dt: datetime) -> datetime:
    """Convert a datetime to GMT+7."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume UTC if no timezone
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(GMT7)


def to_iso_gmt7(dt: datetime) -> str:
    """Convert datetime to ISO string with GMT+7 timezone."""
    if dt is None:
        return None
    gmt7_dt = to_gmt7(dt)
    return gmt7_dt.isoformat()
