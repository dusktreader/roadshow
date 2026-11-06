from pytest import CaptureFixture
from roadshow.main import __version__, main


def test_main_prints_the_version(capsys: CaptureFixture[str]):
    main()

    assert capsys.readouterr().out == f"roadshow {__version__}\n"
