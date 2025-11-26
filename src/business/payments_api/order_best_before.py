from datetime import datetime, timedelta, timezone


def order_best_before(hours: int = 72) -> int:
    now = datetime.now(timezone.utc)
    future = now + timedelta(hours=int(hours))
    return int(future.timestamp())
    