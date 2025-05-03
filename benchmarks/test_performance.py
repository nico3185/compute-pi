"""Performance benchmarks for π calculation."""

import pytest

from compute_pi import PiCalculator


@pytest.mark.benchmark(
    group="precision",
    min_rounds=3,
    max_time=0.5,
)
@pytest.mark.parametrize("precision", [10, 100, 1000])
def test_pi_calculation_precision(benchmark, precision):
    """Benchmark π calculation with different precision levels."""

    def run_calculation():
        calculator = PiCalculator(precision=precision)
        return calculator.compute_pi()

    result = benchmark(run_calculation)
    assert result.correct_digits >= precision


@pytest.mark.benchmark(
    group="progress_tracking",
    min_rounds=3,
    max_time=0.5,
)
def test_pi_calculation_with_progress(benchmark):
    """Benchmark π calculation with progress tracking."""

    def progress_callback(p):
        pass  # Minimal overhead progress tracking

    def run_calculation():
        calculator = PiCalculator(precision=500)
        return calculator.compute_pi(progress_callback=progress_callback)

    result = benchmark(run_calculation)
    assert result.correct_digits >= 500


@pytest.mark.benchmark(
    group="validation",
    min_rounds=3,
    max_time=0.5,
)
def test_result_validation(benchmark):
    """Benchmark result validation performance."""
    calculator = PiCalculator(precision=500)
    result = calculator.compute_pi()

    def validate():
        return calculator._validate_result(result.value)

    correct_digits = benchmark(validate)
    assert correct_digits >= 500


@pytest.mark.benchmark(
    group="memory",
    min_rounds=3,
    max_time=0.5,
)
def test_memory_usage(benchmark):
    """Benchmark memory usage during calculation."""
    import os

    import psutil

    def measure_calculation():
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss

        calculator = PiCalculator(precision=500)
        calculator.compute_pi()

        mem_after = process.memory_info().rss
        return (mem_after - mem_before) / 1024 / 1024  # MB

    mem_usage = benchmark(measure_calculation)
    assert mem_usage > 0  # Should use some memory
