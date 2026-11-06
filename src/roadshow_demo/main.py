from roadshow import Roadshow


def main() -> None:
    roadshow = Roadshow(__package__ or "roadshow_demo", title="roadshow")
    roadshow.run()


if __name__ == "__main__":
    main()
