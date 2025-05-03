"""Tests for edge cases in the compute-pi package."""

import os
from unittest.mock import patch

import pytest

from compute_pi import PiCalculator


def test_minimum_precision():
    """Test computation with minimum valid precision."""
    calculator = PiCalculator(precision=1)
    result = calculator.compute_pi()
    assert result.correct_digits >= 1
    assert str(result.value).startswith("3.1")


def test_maximum_precision():
    """Test computation with very high precision."""
    # Test with a reasonably high precision that won't take too long
    calculator = PiCalculator(precision=10000)
    result = calculator.compute_pi()
    assert result.correct_digits >= 10000
    assert len(str(result.value)) > 10000


def test_precision_validation():
    """Test precision validation."""
    with pytest.raises(ValueError):
        PiCalculator(precision=0)

    with pytest.raises(ValueError):
        PiCalculator(precision=-100)

    calculator = PiCalculator(precision=100)
    with pytest.raises(ValueError):
        calculator.compute_pi(precision=0)


def test_result_formatting():
    """Test result formatting with edge cases."""
    calculator = PiCalculator(precision=50)  # Reduced from 100
    result = calculator.compute_pi()

    # Test with different show_digits values
    edge_cases = [
        1,  # Minimum
        result.correct_digits,  # Exact number of correct digits
        result.correct_digits + 1,  # One more than correct digits
        result.correct_digits * 2,  # Double correct digits
    ]

    # Test interactive terminal output
    with patch("sys.stdout.isatty", return_value=True), patch(
        "os.path.exists", return_value=False
    ), patch.dict(os.environ, {"DOCKER_CONTAINER": "false"}):
        for show_digits in edge_cases:
            formatted = calculator.format_result(result, show_digits=show_digits)
            assert "π Computation Results:" in formatted
            assert str(show_digits) in formatted
            displayed_digits = formatted.split("\n")[1].split(": ")[1]
            assert len(displayed_digits) >= min(show_digits + 2, len(str(result.value)))
            # Check for fancy formatting
            assert "└" in formatted or "│" in formatted

    # Test non-interactive/Docker output
    with patch("sys.stdout.isatty", return_value=False):
        for show_digits in edge_cases:
            formatted = calculator.format_result(result, show_digits=show_digits)
            assert "π Computation Results:" in formatted
            assert str(show_digits) in formatted
            # Check for plain text formatting
            assert "└" not in formatted
            assert "│" not in formatted
            # Verify content is still present
            assert str(result.value)[: show_digits + 2] in formatted
            assert f"{result.computation_time:.2f} seconds" in formatted
            assert str(result.precision) in formatted
            assert str(result.correct_digits) in formatted


def test_precision_override_edge_cases():
    """Test precision override edge cases."""
    calculator = PiCalculator(precision=1000)

    # Test with same precision
    result1 = calculator.compute_pi(precision=1000)
    assert result1.precision == 1000

    # Test with lower precision
    result2 = calculator.compute_pi(precision=100)
    assert result2.precision == 100
    assert result2.correct_digits >= 100

    # Test with higher precision
    result3 = calculator.compute_pi(precision=2000)
    assert result3.precision == 2000
    assert result3.correct_digits >= 2000


def test_string_representation():
    """Test string representation of PiComputationResult."""
    calculator = PiCalculator(precision=10)
    result = calculator.compute_pi()

    # Test direct string conversion
    result_str = str(result)
    assert result_str.startswith("3.14159")
    assert result_str == str(result.value)

    # Test in formatted output
    formatted = calculator.format_result(result, show_digits=5)
    assert "3.14159" in formatted
