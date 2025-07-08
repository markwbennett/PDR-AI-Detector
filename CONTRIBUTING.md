# Contributing to PDR AI Detector

Thank you for your interest in contributing to the PDR AI Detector project! This document provides guidelines for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/PDR-AI-Detector.git
   cd "PDR AI Detector"
   ```
3. **Set up the development environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

### Testing
- Test your changes with the test script: `./test_scraper.py`
- Ensure the scraper works on sample cases before submitting
- Test error handling scenarios

### Documentation
- Update README.md if you add new features
- Update CHANGELOG.md with your changes
- Comment complex logic clearly

## Types of Contributions

### Bug Reports
When reporting bugs, please include:
- Steps to reproduce the issue
- Expected vs actual behavior
- Error messages or logs
- Your environment (OS, Python version)

### Feature Requests
- Describe the feature and its use case
- Explain why it would be valuable
- Consider implementation complexity

### Code Contributions
- Fix bugs or implement new features
- Improve error handling
- Optimize performance
- Add new document types or courts

## Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write clean, well-documented code
   - Test your changes thoroughly
   - Update documentation as needed

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**:
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Provide a clear description of your changes

## Code Review Process

- All submissions require review before merging
- Reviewers will check for:
  - Code quality and style
  - Functionality and testing
  - Documentation updates
  - Compatibility with existing code

## Specific Areas for Contribution

### High Priority
- Additional error handling scenarios
- Support for more document types
- Performance optimizations
- Better progress reporting

### Medium Priority
- GUI interface
- Configuration file support
- Logging improvements
- Additional test cases

### Low Priority
- Support for other courts
- Database storage options
- Advanced filtering options

## Technical Considerations

### Web Scraping Ethics
- Maintain respectful delays between requests
- Don't overwhelm the server
- Respect robots.txt and terms of service
- Consider the impact on server resources

### Error Handling
- Use try-except blocks appropriately
- Provide meaningful error messages
- Implement proper retry logic
- Log errors for debugging

### Performance
- Minimize memory usage
- Use efficient data structures
- Consider concurrent processing carefully
- Profile code changes for performance impact

## Questions or Help

If you have questions about contributing:
- Open an issue on GitHub
- Check existing issues and pull requests
- Review the README.md for technical details

## Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Help maintain a welcoming environment
- Follow GitHub's community guidelines

## License

By contributing to this project, you agree that your contributions will be licensed under the same terms as the project. 