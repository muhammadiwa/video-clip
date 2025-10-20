# 🤝 Contributing to Viral Clip AI Generator

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- FFmpeg
- Basic knowledge of Python and video processing

### Development Setup

1. **Fork and Clone**
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/video-clip.git
cd video-clip
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Run Tests**
```bash
python -m unittest discover tests
```

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Error messages or logs

### Suggesting Features

For feature requests:

- Explain the use case
- Describe the expected behavior
- Provide examples if possible
- Consider implementation complexity

### Pull Requests

1. **Create a Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

2. **Make Changes**
- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation if needed

3. **Test Your Changes**
```bash
# Run tests
python -m unittest discover tests

# Test CLI commands
python cli.py --help
```

4. **Commit Changes**
```bash
git add .
git commit -m "feat: add new feature" # or "fix: resolve bug"
```

Use conventional commit messages:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test updates
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

5. **Push and Create PR**
```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Link to related issues
- Screenshots/videos if applicable

## Code Style

### Python Style

Follow PEP 8 guidelines:

```python
# Good
def process_video(video_path: str, duration: int = 60) -> dict:
    """Process a video and return metadata.
    
    Args:
        video_path: Path to video file
        duration: Target duration in seconds
        
    Returns:
        Dictionary with video metadata
    """
    result = {}
    # Implementation
    return result

# Bad
def process_video(video_path,duration=60):
    result={}
    return result
```

### Documentation

- Add docstrings to all functions and classes
- Use type hints
- Keep comments clear and concise
- Update README for user-facing changes

### Testing

- Add tests for new features
- Ensure existing tests pass
- Test edge cases
- Mock external services (APIs, network)

## Project Structure

```
video-clip/
├── src/                    # Source code
│   ├── downloader/        # Video downloading
│   ├── processor/         # Video processing
│   ├── generator/         # Content generation
│   └── utils/             # Utilities
├── tests/                 # Test files
├── output/                # Generated files (gitignored)
├── cli.py                 # CLI interface
├── README.md              # Main documentation
└── requirements.txt       # Dependencies
```

## Adding New Features

### Adding a New Video Source

1. Create a new file in `src/downloader/`
2. Implement the downloader class
3. Add tests
4. Update CLI to support new source
5. Document in README

Example:
```python
# src/downloader/tiktok.py
class TikTokDownloader:
    def download(self, url: str) -> dict:
        # Implementation
        pass
```

### Adding New Processing Feature

1. Create or update file in `src/processor/`
2. Implement the feature
3. Add tests
4. Update main.py if needed
5. Document usage

### Adding New Content Generator

1. Create or update file in `src/generator/`
2. Implement the generator
3. Add fallback for when API is not available
4. Add tests
5. Document configuration

## Testing Guidelines

### Unit Tests

```python
import unittest
from src.utils.config import Config

class TestConfig(unittest.TestCase):
    def test_config_values(self):
        self.assertIsNotNone(Config.MIN_CLIP_DURATION)
        self.assertEqual(Config.MIN_CLIP_DURATION, 30)
```

### Integration Tests

Mock external services to avoid API costs:

```python
from unittest.mock import patch, MagicMock

class TestYouTubeDownloader(unittest.TestCase):
    @patch('yt_dlp.YoutubeDL')
    def test_download(self, mock_ytdl):
        # Test implementation
        pass
```

## Documentation

Update documentation when:

- Adding new features
- Changing existing behavior
- Adding new dependencies
- Changing configuration options

Files to update:
- `README.md` - Main documentation
- `QUICKSTART.md` - Quick start guide
- Docstrings - Code documentation
- `.env.example` - Configuration example

## Code Review Process

All contributions go through code review:

1. **Automated Checks**
   - Tests must pass
   - Code style checks
   - No security vulnerabilities

2. **Manual Review**
   - Code quality
   - Documentation
   - Test coverage
   - Performance impact

3. **Approval**
   - At least one maintainer approval
   - All comments addressed
   - No merge conflicts

## Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Give constructive feedback
- Celebrate contributions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open an issue for questions
- Tag maintainers if urgent
- Check existing issues first

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions

Thank you for contributing! 🎉
