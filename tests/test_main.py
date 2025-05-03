"""Tests for the command-line interface."""

import logging
import sys
from io import StringIO
from typing import Any, List, Tuple
from unittest.mock import MagicMock, patch

import pytest
from tqdm.auto import tqdm

from compute_pi.logger import TqdmLoggingHandler
from compute_pi.main import create_progress_bar, main, progress_callback


def test_create_progress_bar() -> None:
    """Test progress bar creation."""
    pbar = create_progress_bar(100)
    assert isinstance(pbar, tqdm)
    assert pbar.total == 100
    assert pbar.desc == "Computing π"
    assert "%" in pbar.unit
    pbar.close()


def test_progress_callback() -> None:
    """Test progress callback updates progress bar correctly."""
    mock_pbar = MagicMock()
    progress_callback(0.5, mock_pbar)
    mock_pbar.n = 50
    mock_pbar.refresh.assert_called_once()


@pytest.mark.parametrize(
    "args,expected_code",
    [
        (["--precision", "100"], 0),
        (["--precision", "1000", "--no-progress"], 0),
        (["--precision", "100", "--show-digits", "50"], 0),
        (["--precision", "-1"], 1),  # Should fail with ValueError
    ],
)
def test_main_with_args(args: List[str], expected_code: int) -> None:
    """Test main function with various command line arguments."""
    with patch.object(sys, "argv", ["compute_pi"] + args):
        with patch("sys.stdout", new=StringIO()) as stdout:
            with patch("sys.stderr", new=StringIO()) as stderr:
                with patch("tqdm.auto.tqdm.write") as mock_write:
                    result = main()

                    assert result == expected_code
                    if expected_code == 0:
                        assert "π Computation Results:" in stdout.getvalue()
                    else:
                        # Check both stderr and tqdm output for error messages
                        error_output = stderr.getvalue() + "".join(
                            str(args[0]) for args, _ in mock_write.call_args_list
                        )
                        assert (
                            "ERROR" in error_output or "Precision must be positive" in error_output
                        )


def test_main_with_logging() -> None:
    """Test main function with different logging configurations."""
    test_cases: List[Tuple[List[str], int]] = [
        (["--verbose"], logging.DEBUG),
        ([], logging.INFO),
    ]

    for args, expected_level in test_cases:
        with patch.object(sys, "argv", ["compute_pi"] + args):
            with patch("compute_pi.main.setup_logger") as mock_setup:
                with patch("sys.stdout", new=StringIO()):
                    with patch("sys.stderr", new=StringIO()):
                        main()
                        mock_setup.assert_called_once()
                        call_args = mock_setup.call_args[1]
                        assert call_args["level"] == expected_level


def test_main_with_file_logging(tmp_path: Any) -> None:
    """Test main function with file logging."""
    log_file = tmp_path / "test.log"
    args = ["--log-file", str(log_file)]

    with patch.object(sys, "argv", ["compute_pi"] + args):
        with patch("sys.stdout", new=StringIO()):
            with patch("sys.stderr", new=StringIO()):
                result = main()
                assert result == 0
                assert log_file.exists()
                log_content = log_file.read_text()
                assert "Starting π computation" in log_content


def test_main_keyboard_interrupt() -> None:
    """Test main function handles keyboard interrupt."""
    with patch.object(sys, "argv", ["compute_pi"]):
        with patch("compute_pi.PiCalculator.compute_pi", side_effect=KeyboardInterrupt):
            with patch("sys.stderr", new=StringIO()) as stderr:
                with patch("tqdm.auto.tqdm.write") as mock_write:
                    result = main()
                    assert result == 130
                    # Check both stderr and tqdm output
                    error_output = stderr.getvalue() + "".join(
                        str(args[0]) for args, _ in mock_write.call_args_list
                    )
                    assert "interrupted by user" in error_output.lower()


def test_main_unexpected_error() -> None:
    """Test main function handles unexpected errors."""
    with patch("compute_pi.main.PiCalculator") as mock_calc:
        mock_calc.side_effect = Exception("Unexpected test error")
        with patch.object(sys, "argv", ["compute_pi"]):
            with patch("sys.stderr", new=StringIO()) as stderr:
                with patch("tqdm.auto.tqdm.write") as mock_write:
                    result = main()
                    assert result == 2
                    # Check both stderr and tqdm output
                    error_output = stderr.getvalue() + "".join(
                        str(args[0]) for args, _ in mock_write.call_args_list
                    )
                    assert "Unexpected error:" in error_output


def test_progress_display() -> None:
    """Test progress display functionality."""
    with patch("compute_pi.main.create_progress_bar") as mock_create_bar:
        mock_pbar = MagicMock()
        mock_create_bar.return_value.__enter__.return_value = mock_pbar

        with patch.object(sys, "argv", ["compute_pi", "--precision", "100"]):
            with patch("sys.stdout", new=StringIO()):
                result = main()
                assert result == 0
                mock_create_bar.assert_called_once()
                assert mock_pbar.refresh.called


def test_tqdm_logging_handler() -> None:
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


def test_cli_entrypoint(tmp_path: Any) -> None:
    """Test the compute-pi CLI entrypoint via subprocess."""
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "compute_pi.main", "--precision", "10", "--show-digits", "5"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "π Computation Results:" in result.stdout
    assert "3.14159" in result.stdout
