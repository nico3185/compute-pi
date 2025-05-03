"""Tests for the logger functionality."""

import logging
import os
import tempfile
from io import StringIO
from unittest.mock import patch

from compute_pi.logger import TqdmLoggingHandler, setup_logger


def test_tqdm_logging_handler():
    """Test TqdmLoggingHandler functionality."""
    handler = TqdmLoggingHandler()
    with patch("tqdm.auto.tqdm.write") as mock_write:
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        handler.emit(record)
        mock_write.assert_called_once()
        assert "Test message" in mock_write.call_args[0][0]


def test_logger_setup_basic():
    """Test basic logger setup."""
    logger = setup_logger(name="test")
    assert logger.name == "test"
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0
    assert any(isinstance(h, logging.Handler) for h in logger.handlers)


def test_logger_setup_with_file():
    """Test logger setup with file output."""
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        try:
            logger = setup_logger(name="test", log_file=temp.name)
            assert len(logger.handlers) == 2
            assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)

            # Test logging to file
            test_message = "Test log message"
            logger.info(test_message)

            # Read the log file
            with open(temp.name, "r") as f:
                log_content = f.read()
            assert test_message in log_content

        finally:
            os.unlink(temp.name)


def test_logger_with_tqdm():
    """Test logger with tqdm integration."""
    logger = setup_logger(name="test", use_tqdm=True)
    assert any(isinstance(h, TqdmLoggingHandler) for h in logger.handlers)

    with patch("tqdm.auto.tqdm.write") as mock_write:
        logger.info("Test message")
        mock_write.assert_called_once()


def test_logger_levels():
    """Test different logging levels."""
    # Create a StringIO handler to capture output
    output = StringIO()
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    # Create logger with our handler
    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    messages = {
        "debug": "Debug message",
        "info": "Info message",
        "warning": "Warning message",
        "error": "Error message",
    }

    # Log messages
    logger.debug(messages["debug"])
    logger.info(messages["info"])
    logger.warning(messages["warning"])
    logger.error(messages["error"])

    # Check output
    log_output = output.getvalue()
    for level, msg in messages.items():
        assert msg in log_output, f"Missing {level} message in output"
        level_prefix = level.upper() + ":"
        assert f"{level_prefix} {msg}" in log_output


def test_logger_formatting():
    """Test log message formatting."""
    logger = setup_logger(name="test", use_tqdm=False)
    handler = logger.handlers[0]

    # Test console format
    assert isinstance(handler.formatter, logging.Formatter)
    assert handler.formatter._fmt == "%(levelname)s: %(message)s"

    # Test file format
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        try:
            logger = setup_logger(name="test", log_file=temp.name)
            file_handler = next(h for h in logger.handlers if isinstance(h, logging.FileHandler))
            assert (
                file_handler.formatter._fmt
                == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        finally:
            os.unlink(temp.name)


def test_logger_handler_cleanup():
    """Test that logger handlers are properly cleaned up."""
    name = "test_cleanup"
    logger = logging.getLogger(name)

    # First setup should create handlers
    setup_logger(name=name)
    initial_handler_count = len(logger.handlers)
    assert initial_handler_count > 0

    # Subsequent setup should remove old handlers first
    setup_logger(name=name)
    assert len(logger.handlers) == initial_handler_count
