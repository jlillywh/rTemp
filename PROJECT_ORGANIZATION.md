# rTemp Project Organization

This document describes the organization of the rTemp project after adding the GoldSim integration example.

## Directory Structure

```
rtemp/
├── rtemp/                          # Core package
│   ├── atmospheric/                # Atmospheric radiation calculations
│   ├── heat_flux/                  # Heat flux calculations
│   ├── solar/                      # Solar position and radiation
│   ├── utils/                      # Utilities and validation
│   └── wind/                       # Wind functions
│
├── tests/                          # Test suite
│   ├── unit/                       # Unit tests
│   ├── property/                   # Property-based tests
│   ├── integration/                # Integration tests
│   └── validation/                 # Validation against VBA
│
├── docs/                           # Documentation
│   ├── validation/                 # Validation results
│   ├── USER_GUIDE.md
│   ├── API_REFERENCE.md
│   ├── CONFIGURATION_GUIDE.md
│   ├── METHOD_SELECTION_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── DEVELOPER_GUIDE.md
│
├── examples/                       # Example applications
│   ├── goldsim_integration/        # GoldSim integration example
│   │   ├── README.md               # Example overview
│   │   ├── rtemp_goldsim_adapter.py
│   │   ├── GSPy_314.json
│   │   ├── INTEGRATION_GUIDE.md
│   │   ├── QUICK_REFERENCE.md
│   │   ├── TROUBLESHOOTING.md
│   │   ├── DEWPOINT_ESTIMATION.md
│   │   ├── WIRING_DIAGRAM.md
│   │   ├── SETUP_CHECKLIST.md
│   │   ├── INPUT_ORDER.md
│   │   ├── cloud_cover_estimation.md
│   │   ├── validate_environment.py
│   │   ├── verify_json_config.py
│   │   ├── setup_goldsim_integration.py
│   │   └── blog_post.html
│   └── README.md                   # Examples index
│
├── README.md                       # Main project README
├── CHANGELOG.md                    # Version history
├── CONTRIBUTING.md                 # Contribution guidelines
├── LICENSE                         # MIT License
├── pyproject.toml                  # Project configuration
├── requirements.txt                # Core dependencies
├── requirements-dev.txt            # Development dependencies
└── cleanup_goldsim_files.py        # Cleanup script for old files
```

## Key Files

### Core Package
- `rtemp/model.py` - Main RTempModel class
- `rtemp/config.py` - Configuration and data models
- `rtemp/constants.py` - Physical constants

### Documentation
- `README.md` - Project overview and quick start
- `docs/USER_GUIDE.md` - Comprehensive user guide
- `docs/API_REFERENCE.md` - Complete API documentation
- `CHANGELOG.md` - Version history and changes

### Examples
- `examples/goldsim_integration/` - Complete GoldSim integration
- `examples/README.md` - Examples index

### Development
- `tests/` - Comprehensive test suite (346 tests)
- `pyproject.toml` - Project metadata and dependencies
- `CONTRIBUTING.md` - Development guidelines

## GoldSim Integration Example

The GoldSim integration example (`examples/goldsim_integration/`) is a complete, production-ready integration that includes:

### Core Files
- `rtemp_goldsim_adapter.py` - Python adapter (12 inputs, 3 outputs)
- `GSPy_314.json` - GSPy configuration for Python 3.14
- `validate_environment.py` - Environment validation
- `verify_json_config.py` - Configuration validation
- `setup_goldsim_integration.py` - Automated setup

### Documentation
- `README.md` - Quick start and overview
- `INTEGRATION_GUIDE.md` - Complete setup guide
- `QUICK_REFERENCE.md` - Input/output reference
- `TROUBLESHOOTING.md` - Common issues
- `DEWPOINT_ESTIMATION.md` - Dewpoint estimation guide
- `WIRING_DIAGRAM.md` - Visual setup guide
- `SETUP_CHECKLIST.md` - Step-by-step checklist
- `INPUT_ORDER.md` - Input order reference
- `cloud_cover_estimation.md` - Cloud cover estimation
- `blog_post.html` - Technical blog post

## Cleanup

To remove old/temporary files from the root directory, run:

```bash
python cleanup_goldsim_files.py
```

This will remove:
- Duplicate adapter files
- Temporary JSON files
- Old documentation files (now in examples/)
- Development task files
- Test files (should be in tests/)

## File Naming Conventions

- `README.md` - Overview and quick start for each directory
- `*_GUIDE.md` - Comprehensive guides
- `*_REFERENCE.md` - Reference documentation
- `*.py` - Python source files
- `*.json` - Configuration files
- `test_*.py` - Test files (in tests/ directory)

## Documentation Organization

Documentation is organized by audience:

1. **Users** - `docs/USER_GUIDE.md`, `docs/CONFIGURATION_GUIDE.md`
2. **Developers** - `docs/DEVELOPER_GUIDE.md`, `CONTRIBUTING.md`
3. **API Reference** - `docs/API_REFERENCE.md`
4. **Examples** - `examples/*/README.md`
5. **Troubleshooting** - `docs/TROUBLESHOOTING.md`, `examples/*/TROUBLESHOOTING.md`

## Version Control

Files tracked in git:
- All source code (`rtemp/`, `tests/`, `examples/`)
- All documentation (`docs/`, `*.md`)
- Configuration files (`pyproject.toml`, `*.json` examples)
- License and contributing guidelines

Files ignored (`.gitignore`):
- Virtual environments (`.venv/`)
- Build artifacts (`*.egg-info/`, `__pycache__/`)
- Test coverage (`.coverage`, `htmlcov/`)
- IDE settings (`.vscode/`, `.idea/`)
- Temporary files (`*.pyc`, `*.pyo`)

## Maintenance

Regular maintenance tasks:
1. Update `CHANGELOG.md` for each release
2. Keep documentation in sync with code changes
3. Add new examples to `examples/` directory
4. Update validation results in `docs/validation/`
5. Review and update dependencies in `pyproject.toml`

## Future Organization

Potential additions:
- `examples/standalone/` - Standalone Python examples
- `examples/calibration/` - Calibration workflows
- `examples/sensitivity/` - Sensitivity analysis
- `benchmarks/` - Performance benchmarks
- `data/` - Example datasets
