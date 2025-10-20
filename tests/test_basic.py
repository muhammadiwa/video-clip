"""Basic tests for the Viral Clip AI Generator."""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import Config
from src.utils.logger import setup_logger


class TestConfig(unittest.TestCase):
    """Test configuration."""
    
    def test_config_values(self):
        """Test that config has expected values."""
        self.assertIsNotNone(Config.MIN_CLIP_DURATION)
        self.assertIsNotNone(Config.MAX_CLIP_DURATION)
        self.assertEqual(Config.MIN_CLIP_DURATION, 30)
        self.assertEqual(Config.MAX_CLIP_DURATION, 360)
    
    def test_target_resolution(self):
        """Test target resolution parsing."""
        width, height = Config.get_target_resolution()
        self.assertEqual(width, 1080)
        self.assertEqual(height, 1920)


class TestLogger(unittest.TestCase):
    """Test logging functionality."""
    
    def test_logger_creation(self):
        """Test that logger can be created."""
        logger = setup_logger("test_logger")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test_logger")


class TestImports(unittest.TestCase):
    """Test that modules can be imported."""
    
    def test_import_modules(self):
        """Test that all modules can be imported."""
        try:
            # Test basic imports
            import src
            import src.utils
            import src.utils.config
            import src.utils.logger
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import modules: {e}")


if __name__ == '__main__':
    unittest.main()
