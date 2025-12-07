# GoldSim-rTemp Integration Documentation Index

This document provides an overview of all documentation files for the GoldSim-rTemp integration.

## Quick Navigation

### For New Users
1. **[Quick Start Guide](QUICKSTART_GUIDE.md)** - Get running in 15 minutes
2. **[Installation Guide](GOLDSIM_INTEGRATION_README.md#installation)** - Detailed installation steps
3. **[Validation Script](validate_environment.py)** - Check your environment

### For Configuration
1. **[REFERENCE_DATE Configuration](GOLDSIM_INTEGRATION_README.md#step-6-configure-reference_date)** - Critical setup step
2. **[GoldSim Model Configuration](GOLDSIM_INTEGRATION_README.md#goldsim-model-configuration)** - External element setup
3. **[JSON Configuration](GOLDSIM_INTEGRATION_README.md#step-5-configure-rtemp_adapterjson)** - GSPy settings

### For Troubleshooting
1. **[Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)** - Comprehensive error solutions
2. **[Common Issues](GOLDSIM_INTEGRATION_README.md#troubleshooting)** - Quick fixes
3. **[Log File Analysis](TROUBLESHOOTING_GUIDE.md#log-file-analysis)** - Diagnostic tools

### For Advanced Users
1. **[Advanced Configuration](GOLDSIM_INTEGRATION_README.md#advanced-configuration)** - Customize behavior
2. **[Performance Tuning](GOLDSIM_INTEGRATION_README.md#performance-considerations)** - Optimize speed
3. **[Design Document](.kiro/specs/goldsim-rtemp-integration/design.md)** - Technical architecture

## Documentation Files

### User Guides

#### QUICKSTART_GUIDE.md
**Purpose**: Get new users up and running quickly  
**Audience**: First-time users  
**Time to complete**: 15 minutes  
**Contents**:
- Step-by-step installation (Python, packages, GSPy)
- Minimal GoldSim model configuration
- Quick validation
- Basic troubleshooting

**When to use**: You're setting up the integration for the first time

---

#### GOLDSIM_INTEGRATION_README.md
**Purpose**: Comprehensive reference documentation  
**Audience**: All users  
**Contents**:
- Complete installation instructions
- Architecture overview with diagrams
- GoldSim model configuration details
- Input/output parameter specifications
- Troubleshooting section
- Advanced configuration options
- Performance expectations

**When to use**: 
- You need detailed information about any aspect
- You're troubleshooting an issue
- You want to customize the integration

---

#### TROUBLESHOOTING_GUIDE.md
**Purpose**: Detailed solutions for common problems  
**Audience**: Users experiencing issues  
**Contents**:
- Quick diagnostic checklist
- Error categories with solutions:
  - Installation and configuration errors
  - Configuration errors
  - Runtime errors
  - Data errors
  - Validation errors
- Diagnostic tools
- Log file analysis
- Manual testing procedures

**When to use**: 
- You're getting an error message
- Results don't match expectations
- Performance is slow
- You need to diagnose an issue

---

### Scripts

#### validate_environment.py
**Purpose**: Automated environment validation  
**Audience**: All users  
**Usage**: `py -3.11 validate_environment.py`  
**Checks**:
- ✅ Python version (3.11 or 3.14, 64-bit)
- ✅ Required packages (numpy, pandas, scipy, rtemp)
- ✅ File presence (adapter script, JSON config)
- ✅ JSON configuration validity
- ✅ Adapter script syntax
- ✅ Test execution with sample data
- ✅ Dry-bed logic test

**When to use**:
- Before running GoldSim for the first time
- After making changes to configuration
- When troubleshooting issues
- To verify installation

**Output**: Pass/fail report with specific issues identified

---

### Configuration Files

#### rtemp_adapter.json
**Purpose**: GSPy configuration  
**Audience**: All users (must configure)  
**Critical settings**:
- `python_path`: Path to Python installation (MUST UPDATE)
- `script_path`: Path to adapter script
- `function_name`: "process_data"
- `log_level`: 0-3 (0=errors only, 3=debug)
- `inputs`: 14 input parameters
- `outputs`: 3 output parameters

**When to modify**:
- Initial setup (update python_path)
- Change log level for debugging
- Add/remove parameters (advanced)

---

#### rtemp_goldsim_adapter.py
**Purpose**: Python adapter implementation  
**Audience**: Advanced users (optional modification)  
**Critical settings**:
- `REFERENCE_DATE`: MUST match GoldSim simulation start date
- `DRY_BED_THRESHOLD`: Water depth threshold (default: 0.01 m)
- `ModelConfiguration`: rTemp calculation methods

**When to modify**:
- Initial setup (update REFERENCE_DATE)
- Change calculation methods (solar, longwave, wind)
- Adjust dry-bed threshold
- Make parameters dynamic

---

### Technical Documentation

#### .kiro/specs/goldsim-rtemp-integration/requirements.md
**Purpose**: Formal requirements specification  
**Audience**: Developers, advanced users  
**Contents**:
- User stories and acceptance criteria
- Input/output specifications
- JSON configuration examples
- Python function templates
- Interface specifications

**When to use**:
- Understanding design decisions
- Implementing modifications
- Validating behavior

---

#### .kiro/specs/goldsim-rtemp-integration/design.md
**Purpose**: Technical design document  
**Audience**: Developers, system integrators  
**Contents**:
- Architecture overview
- Component interfaces
- Data models
- Correctness properties
- Error handling strategy
- Testing strategy
- Performance considerations
- Deployment procedures

**When to use**:
- Understanding system architecture
- Implementing modifications
- Troubleshooting complex issues
- Performance optimization

---

#### .kiro/specs/goldsim-rtemp-integration/tasks.md
**Purpose**: Implementation task list  
**Audience**: Developers  
**Contents**:
- Numbered task list with sub-tasks
- Requirements references
- Implementation status

**When to use**:
- Tracking implementation progress
- Understanding what has been implemented

---

## Common Workflows

### First-Time Setup
1. Read [Quick Start Guide](QUICKSTART_GUIDE.md)
2. Follow installation steps
3. Run [validate_environment.py](validate_environment.py)
4. Configure GoldSim model
5. Test with minimal example

### Troubleshooting an Error
1. Check [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
2. Search for your error message
3. Follow diagnostic steps
4. Apply solutions
5. Run [validate_environment.py](validate_environment.py) to verify fix

### Customizing the Integration
1. Read [Advanced Configuration](GOLDSIM_INTEGRATION_README.md#advanced-configuration)
2. Review [Design Document](.kiro/specs/goldsim-rtemp-integration/design.md)
3. Modify configuration files
4. Test changes
5. Run [validate_environment.py](validate_environment.py)

### Performance Optimization
1. Read [Performance Expectations](GOLDSIM_INTEGRATION_README.md#performance-expectations)
2. Set `log_level: 0` in JSON
3. Verify `enable_diagnostics: False` in adapter
4. Profile execution time
5. See [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#error-slow-performance)

## File Organization

```
project_directory/
├── Documentation/
│   ├── DOCUMENTATION_INDEX.md          (this file)
│   ├── QUICKSTART_GUIDE.md             (15-minute setup)
│   ├── GOLDSIM_INTEGRATION_README.md   (comprehensive guide)
│   └── TROUBLESHOOTING_GUIDE.md        (error solutions)
│
├── Scripts/
│   ├── validate_environment.py         (validation script)
│   ├── rtemp_goldsim_adapter.py        (adapter implementation)
│   └── rtemp_adapter.json              (GSPy configuration)
│
├── Specifications/
│   └── .kiro/specs/goldsim-rtemp-integration/
│       ├── requirements.md             (formal requirements)
│       ├── design.md                   (technical design)
│       └── tasks.md                    (implementation tasks)
│
└── GoldSim/
    ├── model.gsm                       (your GoldSim model)
    ├── rtemp_adapter.dll               (GSPy DLL)
    └── results/
        └── rtemp_adapter.log           (execution log)
```

## Documentation Standards

### File Naming
- User guides: `UPPERCASE_GUIDE.md`
- Scripts: `lowercase_script.py`
- Specifications: `lowercase.md`

### Markdown Formatting
- Headers: Use `#` for hierarchy
- Code blocks: Use triple backticks with language
- Tables: Use for structured data
- Lists: Use for sequential steps or options
- Emphasis: Use **bold** for critical information

### Cross-References
- Use relative links: `[text](file.md#section)`
- Link to specific sections when possible
- Provide context for links

## Version Information

- **Documentation Version**: 1.0
- **Last Updated**: 2024-12-06
- **rTemp Version**: 1.0.0
- **GSPy Version**: 1.8.8
- **Python Version**: 3.11 or 3.14

## Getting Help

If you can't find what you need in the documentation:

1. **Check the index**: Use Ctrl+F to search this file
2. **Search documentation**: Use Ctrl+F in individual files
3. **Run validation**: `py -3.11 validate_environment.py`
4. **Check log file**: `rtemp_adapter.log` for error details
5. **Review examples**: See minimal example in Quick Start Guide

## Contributing to Documentation

If you find errors or have suggestions:

1. Note the file name and section
2. Describe the issue or improvement
3. Provide context (what you were trying to do)
4. Include any error messages or screenshots

## License

This documentation follows the same license as the rTemp package.

---

**Quick Links**:
- [Quick Start](QUICKSTART_GUIDE.md) | [Full Guide](GOLDSIM_INTEGRATION_README.md) | [Troubleshooting](TROUBLESHOOTING_GUIDE.md) | [Validation](validate_environment.py)
