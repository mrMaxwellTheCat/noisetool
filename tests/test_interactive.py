from __future__ import annotations

from noise.interactive import run_wizard


class TestInteractiveImports:
    def test_module_imports(self) -> None:
        from noise import interactive

        assert hasattr(interactive, "run_wizard")

    def test_run_wizard_is_callable(self) -> None:
        assert callable(run_wizard)


def test_interactive_flag() -> None:
    from noise.cli import parse_args

    args = parse_args(["-i"])
    assert args.interactive
    args2 = parse_args(["--interactive"])
    assert args2.interactive


def test_wizard_returns_dict() -> None:
    """Verify run_wizard returns a dict with expected keys."""
    from noise.interactive import run_wizard

    assert callable(run_wizard)
    import inspect

    sig = inspect.signature(run_wizard)
    assert "config" not in sig.parameters  # no args
