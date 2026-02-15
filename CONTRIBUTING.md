# Contributing to Financial Reporting Engine

Thank you for considering contributing to the Universal Financial Reporting Engine! 

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:

1. **Clear title** - Describe the issue briefly
2. **Steps to reproduce** - How can we recreate the bug?
3. **Expected behavior** - What should happen?
4. **Actual behavior** - What actually happens?
5. **Environment** - Python version, OS, package versions
6. **Sample data** - If possible, a minimal CSV that triggers the bug

### Suggesting Features

We welcome feature suggestions! Please open an issue with:

1. **Use case** - What problem does this solve?
2. **Proposed solution** - How should it work?
3. **Alternatives** - Other approaches you considered
4. **Examples** - Mock-ups or examples if applicable

### Pull Requests

#### Before You Start

1. **Check existing issues** - Someone may already be working on it
2. **Discuss major changes** - Open an issue first for big features
3. **Fork the repository** - Work on your own fork
4. **Create a branch** - Use descriptive names (e.g., `feature/add-quarterly-support`)

#### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/financial-reporting-engine.git
cd financial-reporting-engine

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pylint black
```

#### Code Standards

- **Python 3.9+** - Use modern Python features
- **PEP 8** - Follow Python style guidelines
- **Type hints** - Add type annotations where helpful
- **Docstrings** - Document all public functions/classes
- **Comments** - Explain complex logic

**Format code with black:**
```bash
black src/
```

**Check with pylint:**
```bash
pylint src/
```

#### Testing

All new features should include tests:

```bash
# Run tests
python -m pytest tests/

# Add a new test
# tests/test_yourfeature.py
```

#### Documentation

Update documentation for new features:

- `README.md` - If it affects usage
- `docs/QUICK_START.md` - If it's a common use case
- `docs/USER_MANUAL.md` - For detailed features
- `docs/API_REFERENCE.md` - For new modules/functions

#### Commit Messages

Write clear commit messages:

```
Add quarterly variance analysis

- Implemented quarter-over-quarter calculations
- Added Q1-Q4 period detection
- Updated tests for quarterly data
```

#### Pull Request Process

1. **Update CHANGELOG.md** - Document your changes
2. **Pass all tests** - Ensure `pytest` passes
3. **Update documentation** - If needed
4. **Submit PR** - With clear description
5. **Respond to feedback** - Address reviewer comments

### Code of Conduct

Be respectful and constructive. We're all here to make this tool better!

### Areas for Contribution

#### High Priority
- [ ] Additional chart types (waterfall, sparklines)
- [ ] Multi-sheet Excel support
- [ ] Interactive HTML reports
- [ ] Quarterly/weekly period support
- [ ] Custom metric formulas

#### Medium Priority
- [ ] SQL database input
- [ ] API endpoints
- [ ] Web dashboard  
- [ ] Email report delivery
- [ ] Scheduled runs

#### Low Priority
- [ ] PowerPoint export
- [ ] Mobile-friendly reports
- [ ] Multi-language support
- [ ] Theme customization

### Questions?

Open a GitHub discussion or comment on an existing issue!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for making this project better! 🎉
