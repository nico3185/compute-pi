"""Logging configuration for the compute-pi package."""

import logging
import sys
from typing import Optional

from tqdm.auto import tqdm


class TqdmLoggingHandler(logging.Handler):
    """Logging handler that writes through tqdm to preserve progress bars."""

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log message through tqdm.write().

        Args:
            record: The log record to emit
        """
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)


def setup_logger(
    name: str = "compute_pi",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    use_tqdm: bool = True,
) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: Logger name (default: compute_pi)
        level: Logging level (default: INFO)
        log_file: Optional file path for logging
        use_tqdm: Whether to use tqdm-compatible logging (default: True)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove any existing handlers
    logger.handlers = []

    # Create formatters
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Console handler (using tqdm if requested)
    if use_tqdm:
        console_handler: logging.Handler = TqdmLoggingHandler()
    else:
        console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler if requested
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to setup file logging to {log_file}: {e}")
            # Don't raise the error - continue with console logging only
            pass

    return logger


# Do NOT instantiate a global logger here.
# Always use logging.getLogger("compute_pi") in your modules.
