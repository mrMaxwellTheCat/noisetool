from __future__ import annotations

from noise.eqviz import plot_filter_response


class TestPlotFilterResponse:
    def test_lowpass(self) -> None:
        result = plot_filter_response("lowpass", [1000], 44100, width=20, height=5)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_highpass(self) -> None:
        result = plot_filter_response("highpass", [100], 44100, width=20, height=5)
        assert isinstance(result, str)

    def test_bandpass(self) -> None:
        result = plot_filter_response("bandpass", [100, 5000], 44100, width=20, height=5)
        assert isinstance(result, str)

    def test_unknown_type(self) -> None:
        result = plot_filter_response("unknown", [], 44100, width=10, height=3)
        assert isinstance(result, str)

    def test_eq_viz_flag(self) -> None:
        from noise.cli import parse_args

        args = parse_args(["--eq-viz"])
        assert args.eq_viz
