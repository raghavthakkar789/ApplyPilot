import signal
import time

running = True


def stop(_signum: int, _frame: object) -> None:
    global running
    running = False


def main() -> None:
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    while running:
        time.sleep(1)


if __name__ == "__main__":
    main()
