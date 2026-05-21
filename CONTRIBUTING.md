# Contributing

Thanks for your interest in contributing to **noisetool**!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/noise.git`
3. Install in dev mode: `pip install -e ".[dev]"`
4. Install pre-commit hooks: `pre-commit install`

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run the full quality check suite:

```bash
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/
pytest tests/ -v --tb=short
```

4. Commit and push: `git commit -m "Description of changes"`
5. Open a Pull Request

## Code Style

- Follow PEP 8 (enforced by ruff)
- Use type annotations for all functions (enforced by mypy strict mode)
- Write tests for new features
- Keep functions focused and small
- Use descriptive variable names

## Testing

- All tests go in the `tests/` directory
- Name test files `test_*.py`
- Use pytest fixtures from `tests/conftest.py`
- Aim for >90% coverage on new code

## Pull Request Guidelines

- Keep PRs focused on a single change
- Update the README if needed
- Ensure CI passes
- Add tests for new functionality
