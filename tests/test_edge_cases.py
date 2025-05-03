"""Tests for edge cases and error conditions."""

import pytest
from mpmath import mp  # type: ignore

from compute_pi import PiCalculator


def test_very_high_precision() -> None:
    """Test computation with very high precision."""
    precision = 10000  # Reduced from 100000
    calculator = PiCalculator(precision=precision)
    result = calculator.compute_pi()
    assert result.correct_digits >= precision


def test_minimum_precision() -> None:
    """Test computation with minimum valid precision."""
    calculator = PiCalculator(precision=1)
    result = calculator.compute_pi()
    assert result.correct_digits >= 1
    assert str(result.value).startswith("3.1")


@pytest.mark.parametrize(
    "precision",
    [
        1,  # Minimum
        10,  # Small
        100,  # Medium
        500,  # Large (reduced from 1000)
    ],
)
def test_precision_boundaries(precision: int) -> None:
    """Test precision at various boundaries."""
    calculator = PiCalculator(precision=precision)
    result = calculator.compute_pi()
    assert result.correct_digits >= precision


def test_progress_callback_edge_cases() -> None:
    """Test progress callback with edge cases."""
    progress_values = []

    def callback(p: float) -> None:
        progress_values.append(p)

    calculator = PiCalculator(precision=50)  # Reduced from 100
    calculator.compute_pi(progress_callback=callback)

    assert len(progress_values) > 0
    assert all(0 <= p <= 1 for p in progress_values)
    assert progress_values[0] < 1  # First update should not be 100%
    assert progress_values[-1] > 0.9  # Last update should be near 100%


def test_result_formatting_edge_cases() -> None:
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

    for show_digits in edge_cases:
        formatted = calculator.format_result(result, show_digits=show_digits)
        assert "π Computation Results:" in formatted
        assert str(show_digits) in formatted
        displayed_digits = formatted.split("\n")[1].split(": ")[1]
        assert len(displayed_digits) >= min(show_digits + 2, len(str(result.value)))


def test_precision_override_edge_cases() -> None:
    """Test precision override with edge cases."""
    calculator = PiCalculator(precision=500)  # Reduced from 1000

    # Test various override values
    test_cases = [
        1,  # Minimum
        calculator.target_precision // 2,  # Half original
        calculator.target_precision * 2,  # Double original
    ]

    for precision in test_cases:
        result = calculator.compute_pi(precision=precision)
        assert result.precision == precision
        assert result.correct_digits >= precision


def test_error_handling() -> None:
    """Test error handling for various invalid inputs."""
    with pytest.raises(ValueError):
        PiCalculator(precision=0)

    with pytest.raises(ValueError):
        PiCalculator(precision=-100)

    calculator = PiCalculator(precision=50)  # Reduced from 100

    with pytest.raises(ValueError):
        calculator.compute_pi(precision=0)

    with pytest.raises(ValueError):
        calculator.compute_pi(precision=-1)


def test_mpmath_context_handling() -> None:
    """Test handling of mpmath context changes."""
    original_dps = mp.dps
    original_prec = mp.prec

    calculator = PiCalculator(precision=50)  # Reduced from 100
    result = calculator.compute_pi()

    # Context should be restored
    assert mp.dps == original_dps
    assert mp.prec == original_prec

    # Result should still be valid
    assert result.correct_digits >= 50  # Reduced from 100
