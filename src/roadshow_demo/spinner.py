from time import sleep

import roadshow


@roadshow.demo("spinner")
def show_output() -> None:
    """
    This demo shows how Roadshow displays a spinner when processing a long-running demo function.

    Roadshow has to run the whole function before it can print results in the demo display. If your demo function takes
    some time, it might appear to a user as if it was frozen. The spinner reassures users that the demo is still working
    correctly.
    """
    print("This is a sloooow function, so a spinner is nice.")
    sleep(3)
