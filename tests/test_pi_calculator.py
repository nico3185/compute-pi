"""Unit tests for the PiCalculator class."""

import pytest
from mpmath import mp

from compute_pi import PiCalculator, PiComputationResult


class TestPiCalculator:
    """Test suite for PiCalculator class."""

    def test_init_with_valid_precision(self) -> None:
        """Test initialization with valid precision."""
        calculator = PiCalculator(precision=1000)
        assert calculator.working_precision == 2000  # double precision
        assert calculator.target_precision == 1000

    def test_init_with_invalid_precision(self) -> None:
        """Test initialization with invalid precision."""
        with pytest.raises(ValueError, match="Precision must be positive"):
            PiCalculator(precision=0)
        with pytest.raises(ValueError, match="Precision must be positive"):
            PiCalculator(precision=-100)

    def test_compute_pi_accuracy(self) -> None:
        """Test that computed π is accurate to requested precision."""
        precision = 100
        calculator = PiCalculator(precision=precision)
        result = calculator.compute_pi()
        assert result.correct_digits >= precision

    def test_compute_pi_with_progress(self) -> None:
        """Test computation with progress tracking."""
        progress_calls = []

        def progress_callback(p: float) -> None:
            progress_calls.append(p)

        calculator = PiCalculator(precision=100)
        calculator.compute_pi(progress_callback=progress_callback)

        assert len(progress_calls) > 0
        assert all(0 <= p <= 1 for p in progress_calls)
        # Progress might not reach exactly 1.0 due to integer division
        assert progress_calls[-1] > 0.9  # Last call should be near completion

    def test_compute_pi_with_override_precision(self) -> None:
        """Test computation with precision override."""
        calculator = PiCalculator(precision=1000)
        result = calculator.compute_pi(precision=100)
        assert result.precision == 100  # Should match requested precision
        assert result.correct_digits >= 100

    def test_compute_pi_invalid_override_precision(self) -> None:
        """Test computation with invalid precision override."""
        calculator = PiCalculator(precision=100)
        with pytest.raises(ValueError, match="Precision must be positive"):
            calculator.compute_pi(precision=0)

    def test_validate_result(self) -> None:
        """Test result validation against known π value."""
        calculator = PiCalculator(precision=100)
        # Test with first 10 digits of π
        test_pi = mp.mpf("3.141592653")
        correct_digits = calculator._validate_result(test_pi)
        assert correct_digits == 9  # 9 digits after decimal point

    def test_format_result(self) -> None:
        """Test result formatting."""
        calculator = PiCalculator(precision=100)
        result = PiComputationResult(
            value=mp.mpf("3.141592653589793"),
            computation_time=1.23,
            precision=100,
            correct_digits=14,
            debug_info={"target_precision": 100, "working_precision": 200, "correct_digits": 14},
        )
        formatted = calculator.format_result(result, show_digits=5)
        assert "3.14159" in formatted
        assert "1.23 seconds" in formatted
        assert "100 digits" in formatted
        assert "14" in formatted

    @pytest.mark.parametrize("precision", [10, 100, 1000])
    def test_different_precisions(self, precision: int) -> None:
        """Test computation with different precisions."""
        calculator = PiCalculator(precision=precision)
        result = calculator.compute_pi()
        assert result.correct_digits >= precision

    def test_first_digits_correctness(self) -> None:
        """Test that first few digits match known π value."""
        calculator = PiCalculator(precision=10)
        result = calculator.compute_pi()
        pi_str = str(result.value)
        assert pi_str.startswith("3.141592653")

    def test_computation_time_tracking(self) -> None:
        """Test that computation time is tracked correctly."""
        calculator = PiCalculator(precision=100)
        result = calculator.compute_pi()
        assert result.computation_time > 0
        assert isinstance(result.computation_time, float)

    def test_debug_info_contents(self) -> None:
        """Test that debug info contains all required fields."""
        calculator = PiCalculator(precision=100)
        result = calculator.compute_pi()
        required_fields = {
            "target_precision",
            "working_precision",
            "mp_dps",
            "mp_prec",
            "n_terms",
            "correct_digits",
        }
        assert all(field in result.debug_info for field in required_fields)
