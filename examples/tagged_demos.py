from roadshow import demo


@demo("reports")
def show_report():
    """Print the latest report."""
    print("Report ready")


@demo("exports")
def export_report():
    """Export the latest report."""
    print("Export ready")


@demo("errors")
def show_failure():
    """Demonstrate a captured exception."""
    raise RuntimeError("Report unavailable")
