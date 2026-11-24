import roadshow


@roadshow.demo("ordering", order=2)
def show_declared_order() -> None:
    """Show that order can override declaration order within a feature."""
    print("This demo was declared first but runs second because it has order=2.")


@roadshow.demo("ordering", order=1)
def show_explicit_order() -> None:
    """Show the first demo in an explicitly ordered group."""
    print("This demo runs first because it has order=1.")


@roadshow.demo("ordering", order=3)
def show_last_order() -> None:
    """Show the last demo in an explicitly ordered group."""
    print("This demo runs third because it has order=3.")


@roadshow.demo("ordering")
def show_default_order() -> None:
    """Show that unordered demos run after explicitly ordered demos."""
    print("This demo runs after the explicitly ordered demos.")
