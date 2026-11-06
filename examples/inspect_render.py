from rich.console import Console
from roadshow import decompose_demo
from roadshow.render import display_demo
from my_app.demos import show_report


details = decompose_demo(show_report)
print(details.source)
display_demo(show_report, Console())
