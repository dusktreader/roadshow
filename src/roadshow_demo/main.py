from roadshow import Roadshow


def main() -> None:
    roadshow = Roadshow(
        __package__ or "roadshow_demo",
        title="roadshow",
        feature_order=("basic", "lifecycle", "capture", "spinner"),
    )
    roadshow.run()


if __name__ == "__main__":
    main()
