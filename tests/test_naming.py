from __future__ import annotations

from noise.cli import parse_args


class TestPattern:
    def test_basic_pattern(self) -> None:
        args = parse_args(["--pattern", "{type}_{format}_{sr}"])
        assert args.pattern == "{type}_{format}_{sr}"


class TestSeeds:
    def test_multiple_seeds(self) -> None:
        args = parse_args(["--seeds", "1,2,3,42,100"])
        seeds = [int(s.strip()) for s in args.seeds.split(",")]
        assert seeds == [1, 2, 3, 42, 100]

    def test_single_seed(self) -> None:
        args = parse_args(["--seeds", "42"])
        seeds = [int(s.strip()) for s in args.seeds.split(",")]
        assert seeds == [42]
