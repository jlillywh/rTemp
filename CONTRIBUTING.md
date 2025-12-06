# Contributing to rTemp

Thank you for your interest in contributing to the rTemp water temperature model!

## Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd rtemp
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

## Code Quality Standards

### Formatting

We use `black` for code formatting and `isort` for import sorting:

```bash
# Format code
black rtemp tests

# Sort imports
isort rtemp tests
```

### Type Checking

We use `mypy` for static type checking:

```bash
mypy rtemp
```

All functions should have type hints for parameters and return values.

### Linting

We use `flake8` for linting:

```bash
flake8 rtemp tests
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit -m unit
pytest tests/property -m property
pytest tests/integration -m integration

# Run with coverage
pytest --cov=rtemp --cov-report=html
```

### Writing Tests

- **Unit Tests**: Test individual functions and classes in isolation
- **Property Tests**: Use Hypothesis for property-based testing
- **Integration Tests**: Test complete model execution

All new features should include appropriate tests.

### Property-Based Testing

When writing property-based tests:

1. Use Hypothesis for generating test inputs
2. Configure tests to run at least 100 iterations
3. Tag tests with comments linking to design properties:
   ```python
   # Feature: rtemp-python-complete, Property X: [description]
   # Validates: Requirements Y.Z
   ```

## Code Organization

- `rtemp/`: Main package code
  - `solar/`: Solar position and radiation calculations
  - `atmospheric/`: Longwave radiation calculations
  - `wind/`: Wind function calculations
  - `heat_flux/`: Heat flux calculations
  - `utils/`: Utility functions
- `tests/`: Test suite
  - `unit/`: Unit tests
  - `property/`: Property-based tests
  - `integration/`: Integration tests
  - `fixtures/`: Test data and fixtures

## Documentation

- Add docstrings to all public classes and methods
- Use Google-style docstrings
- Include type hints in function signatures
- Update README.md for user-facing changes

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Run all tests and quality checks
4. Update documentation as needed
5. Submit a pull request with a clear description

## Questions?

Open an issue on GitHub for questions or discussions.
