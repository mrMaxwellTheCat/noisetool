from __future__ import annotations

from pathlib import Path

from noise.cli import parse_args


class TestInfoFlag:
    def test_info_flag_parsing(self) -> None:
        args = parse_args(["--info", "test.wav"])
        assert args.info == Path("test.wav")
        assert isinstance(args.info, Path)
