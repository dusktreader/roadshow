import sys

from roadshow import demo


@demo("greetings", input_text="Ada\n", argv=("--formal",))
def greet():
    """Greet a name supplied through standard input."""
    print(f"Hello, {input()}.")
    print(sys.argv[1:])
