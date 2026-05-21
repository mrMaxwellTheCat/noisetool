from __future__ import annotations

from noise.cli import parse_args


class TestSilentMode:
    def test_flag_parses(self) -> None:
        args = parse_args(["--silent"])
        assert args.silent
