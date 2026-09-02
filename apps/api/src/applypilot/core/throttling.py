BACKOFF_SECONDS = {5: 30, 6: 60, 7: 120, 8: 240, 9: 480}


def login_delay_seconds(failure_count: int) -> int:
    if failure_count < 5:
        return 0
    return BACKOFF_SECONDS.get(failure_count, 900)
