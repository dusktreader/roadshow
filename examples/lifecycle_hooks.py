from roadshow import demo


def announce_start():
    print("Starting demo")


def announce_finish():
    print("Finished demo")


@demo("greetings", before=announce_start, after=announce_finish)
def greet():
    """Print a greeting."""
    print("Hello")
