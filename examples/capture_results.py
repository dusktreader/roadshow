from my_app.demos import show_report
from roadshow import capture_demo

result = capture_demo(show_report)
if result.stdout:
    print(result.stdout, end="")
if not result.succeeded:
    print(result.error or result.exit_code)
