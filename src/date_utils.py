from datetime import datetime, timezone

def ms2utcstr(ms: int | float) -> str:
    """
    Returns a datetime string in UTC from a timestamp in milliseconds.

    Args:
        ms (int | float): Timestamp in milliseconds.

    Returns:
        str: Datetime string in UTC
    """
    return datetime.fromtimestamp(
        ms/1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')

