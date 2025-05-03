"""Tests for the command-line interface."""

import sys
import logging
import os
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from tqdm.auto import tqdm

from compute_pi.main import create_progress_bar, main, progress_callback, is_non_interactive
from compute_pi.logger import TqdmLoggingHandler


def test_create_progress_bar():
    """Test progress bar creation."""
    pbar = create_progress_bar(100)
    assert isinstance(pbar, tqdm)
    assert pbar.total == 100
    assert pbar.desc == "Computing π"
    assert "%" in pbar.unit
    pbar.close()


def test_is_non_interactive():
    """Test non-interactive environment detection."""
    with patch('sys.stdout.isatty', return_value=False):
        assert is_non_interactive()
    
    with patch('os.path.exists', return_value=True):
        assert is_non_interactive()
    
    with patch.dict(os.environ, {'DOCKER_CONTAINER': 'true'}):
        assert is_non_interactive()
    
    with patch('sys.stdout.isatty', return_value=True), \
         patch('os.path.exists', return_value=False), \
         patch.dict(os.environ, {'DOCKER_CONTAINER': 'false'}):
        assert not is_non_interactive()


@pytest.mark.parametrize("args,expected_code", [
    (["--precision", "100"], 0),
    (["--precision", "1000", "--no-progress"], 0),
    (["--precision", "100", "--show-digits", "50"], 0),
    (["--precision", "-1"], 1),  # Should fail with ValueError
    (["--precision", "100", "--plain"], 0),  # Test plain output
])
def test_main_with_args(args, expected_code):
    """Test main function with various command line arguments."""
    with patch.object(sys, 'argv', ['compute_pi'] + args):
        with patch('sys.stdout', new=StringIO()) as stdout:
            with patch('sys.stderr', new=StringIO()) as stderr:
                with patch('tqdm.auto.tqdm.write') as mock_write:
                    result = main()
                    
                    assert result == expected_code
                    if expected_code == 0:
                        output = stdout.getvalue()
                        assert "π Computation Results:" in output
                        if "--plain" in args:
                            # Check for plain text formatting
                            assert "└" not in output
                            assert "│" not in output
                        elif not is_non_interactive():
                            # Check for fancy formatting in interactive mode
                            assert any(c in output for c in "└│")
                    else:
                        # Check both stderr and tqdm output for error messages
                        error_output = stderr.getvalue() + ''.join(str(args[0]) for args, _ in mock_write.call_args_list)
                        assert "ERROR" in error_output or "Precision must be positive" in error_output


def test_main_with_logging():
    """Test main function with different logging configurations."""
    test_cases = [
        (["--verbose"], logging.DEBUG),
        ([], logging.INFO),
    ]
    
    for args, expected_level in test_cases:
        with patch.object(sys, 'argv', ['compute_pi'] + args):
            with patch('compute_pi.main.setup_logger') as mock_setup:
                with patch('sys.stdout', new=StringIO()):
                    with patch('sys.stderr', new=StringIO()):
                        main()
                        mock_setup.assert_called_once()
                        call_args = mock_setup.call_args[1]
                        assert call_args['level'] == expected_level


def test_main_with_file_logging(tmp_path):
    """Test main function with file logging."""
    log_file = tmp_path / "test.log"
    args = ["--log-file", str(log_file)]
    
    with patch.object(sys, 'argv', ['compute_pi'] + args):
        with patch('sys.stdout', new=StringIO()):
            with patch('sys.stderr', new=StringIO()):
                result = main()
                assert result == 0
                assert log_file.exists()
                log_content = log_file.read_text()
                assert "Starting π computation" in log_content


def test_main_keyboard_interrupt():
    """Test main function handles keyboard interrupt."""
    with patch.object(sys, 'argv', ['compute_pi']):
        with patch('compute_pi.PiCalculator.compute_pi', side_effect=KeyboardInterrupt):
            with patch('sys.stderr', new=StringIO()) as stderr:
                with patch('tqdm.auto.tqdm.write') as mock_write:
                    result = main()
                    assert result == 130
                    # Check both stderr and tqdm output
                    error_output = stderr.getvalue() + ''.join(str(args[0]) for args, _ in mock_write.call_args_list)
                    assert "interrupted by user" in error_output.lower()


def test_main_unexpected_error():
    """Test main function handles unexpected errors."""
    with patch('compute_pi.main.PiCalculator') as mock_calc:
        mock_calc.side_effect = Exception("Unexpected test error")
        with patch.object(sys, 'argv', ['compute_pi']):
            with patch('sys.stderr', new=StringIO()) as stderr:
                with patch('tqdm.auto.tqdm.write') as mock_write:
                    result = main()
                    assert result == 2
                    # Check both stderr and tqdm output
                    error_output = stderr.getvalue() + ''.join(str(args[0]) for args, _ in mock_write.call_args_list)
                    assert "Unexpected error:" in error_output


def test_progress_display():
    """Test progress display functionality."""
    with patch('compute_pi.main.create_progress_bar') as mock_create_bar, \
         patch('compute_pi.main.is_non_interactive', return_value=False):
        mock_pbar = MagicMock()
        mock_create_bar.return_value.__enter__.return_value = mock_pbar
        
        with patch.object(sys, 'argv', ['compute_pi', '--precision', '100']):
            with patch('sys.stdout', new=StringIO()):
                result = main()
                assert result == 0
                mock_create_bar.assert_called_once()
                assert mock_pbar.refresh.called


def test_tqdm_logging_handler():
    """Test TqdmLoggingHandler functionality."""
    handler = TqdmLoggingHandler()
    with patch('tqdm.auto.tqdm.write') as mock_write:
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        handler.emit(record)
        mock_write.assert_called_once()
        assert "Test message" in mock_write.call_args[0][0]


def test_cli_entrypoint(tmp_path):
    """Test the compute-pi CLI entrypoint via subprocess."""
    import subprocess
    
    # Test with plain output
    result = subprocess.run([
        sys.executable, '-m', 'compute_pi.main',
        '--precision', '10',
        '--show-digits', '5',
        '--plain'
    ], capture_output=True, text=True)
    assert result.returncode == 0
    assert "π Computation Results:" in result.stdout
    assert "3.14159" in result.stdout
    assert "└" not in result.stdout  # No fancy formatting
    
    # Test with default output in non-interactive mode
    result = subprocess.run([
        sys.executable, '-m', 'compute_pi.main',
        '--precision', '10',
        '--show-digits', '5'
    ], capture_output=True, text=True)
    assert result.returncode == 0
    assert "π Computation Results:" in result.stdout
    assert "3.14159" in result.stdout 