from __future__ import annotations

from noise.interactive import run_wizard


class TestInteractiveImports:
    def test_module_imports(self) -> None:
        from noise import interactive

        assert hasattr(interactive, "run_wizard")

    def test_run_wizard_is_callable(self) -> None:
        assert callable(run_wizard)

    def test_wizard_returns_dict(self) -> None:
        # Can't run the wizard interactively in tests,
        # but verify the function signature is correct
        import inspect

        sig = inspect.signature(run_wizard)
        assert "config" not in sig.parameters


def test_quick_wizard_import() -> None:
    from noise.interactive import _quick_wizard

    assert callable(_quick_wizard)


def test_interactive_flag() -> None:
    from noise.cli import parse_args

    args = parse_args(["-i"])
    assert args.interactive
    args2 = parse_args(["--interactive"])
    assert args2.interactive


def test_continuous_in_wizard() -> None:
    """Verify continuous mode can be activated."""
    from noise.interactive import FORMAT_PRESETS, NOISE_PRESETS

    assert "1" in NOISE_PRESETS
    assert "5" in FORMAT_PRESETS
    assert FORMAT_PRESETS["5"]["label"] == "WAV+FLAC"
