"""Module for high-precision calculation of π using the Chudnovsky algorithm."""

import os
import sys
from dataclasses import dataclass
from time import time
from typing import Any, Callable, Dict, Optional

from mpmath import mp

from .logger import logger


@dataclass
class PiComputationResult:
    """Result of a π computation including metadata."""

    value: mp.mpf
    computation_time: float
    precision: int
    correct_digits: int
    debug_info: Dict[str, Any]

    def __str__(self) -> str:
        """Return a string representation of the result."""
        return str(self.value)


class PiCalculator:
    """Calculator for high-precision π computation using the Chudnovsky algorithm."""

    def __init__(self, precision: int = 10000):
        """
        Initialize the calculator with desired precision.

        Args:
            precision: Number of decimal places to compute (default: 10000)

        Raises:
            ValueError: If precision is not positive
        """
        if precision <= 0:
            logger.error(f"Invalid precision value: {precision}")
            raise ValueError("Precision must be positive")

        logger.info(f"Initializing calculator with precision {precision}")

        # Add a larger buffer to account for intermediate calculations
        self.target_precision = precision
        self.working_precision = max(precision * 2, 10)  # Ensure minimum working precision
        mp.dps = self.working_precision
        # Create a fresh context with our precision
        mp.prec = mp.dps * 4  # Increase binary precision

        # Cache some constants
        self._reference_pi = mp.pi
        self._C = mp.mpf(426880) * mp.sqrt(mp.mpf(10005))

        logger.debug(f"Working precision set to {self.working_precision}")
        logger.debug(f"Binary precision set to {mp.prec}")

    def compute_pi(
        self,
        precision: Optional[int] = None,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> PiComputationResult:
        """
        Compute π using the Chudnovsky algorithm.

        Args:
            precision: Override the instance precision if provided
            progress_callback: Optional callback function(progress: float) for progress updates

        Returns:
            PiComputationResult containing the computed value and metadata

        Raises:
            ValueError: If precision is not positive
        """
        if precision is not None:
            if precision <= 0:
                logger.error(f"Invalid precision override: {precision}")
                raise ValueError("Precision must be positive")
            self.target_precision = precision
            self.working_precision = max(precision * 2, 10)  # Ensure minimum working precision
            mp.dps = self.working_precision
            mp.prec = mp.dps * 4
            logger.info(f"Precision overridden to {precision}")

        start_time = time()
        logger.info("Starting π computation")

        # Calculate number of terms needed (~14.18 digits per term)
        n_terms = max(int(self.target_precision / 14.181647462) + 3, 5)  # Minimum 5 terms

        debug_info = {
            "target_precision": self.target_precision,
            "working_precision": self.working_precision,
            "mp_dps": mp.dps,
            "mp_prec": mp.prec,
            "n_terms": n_terms,
        }

        logger.debug("Computation parameters:", extra=debug_info)

        # Use mpmath's context manager to ensure high precision
        with mp.workprec(int(mp.prec)):
            M = mp.mpf(1)
            L = mp.mpf(13591409)
            X = mp.mpf(1)
            K = 6
            S = L

            for k in range(1, n_terms):
                # Convert to mpf for proper division
                k3 = mp.mpf(k * k * k)
                K3 = K * K * K
                M = M * (K3 - 16 * K) / k3
                L += 545140134
                X *= -262537412640768000
                term = (M * L) / X
                S += term
                K += 12

                if progress_callback:
                    progress = (k + 1) / n_terms  # Adjust to reach 1.0
                    progress_callback(progress)
                    logger.debug(f"Progress: {progress:.1%}")

            result = self._C / S

            # Add intermediate values to debug info
            debug_info.update(
                {
                    "M_len": len(str(M)),
                    "X_len": len(str(X)),
                    "S_len": len(str(S)),
                    "result_len": len(str(result)),
                }
            )

        computation_time = time() - start_time
        logger.info(f"Computation completed in {computation_time:.2f} seconds")

        # Validate result
        correct_digits = self._validate_result(result)
        debug_info["correct_digits"] = correct_digits
        logger.info(f"Validated {correct_digits} correct digits")

        return PiComputationResult(
            value=result,
            computation_time=computation_time,
            precision=self.target_precision,
            correct_digits=correct_digits,
            debug_info=debug_info,
        )

    def _validate_result(self, computed_pi: mp.mpf) -> int:
        """
        Validate the computed π against a reference value.

        Returns:
            Number of correct decimal digits
        """
        # Convert to strings with extra precision to ensure accurate comparison
        computed_str = str(computed_pi)
        reference_str = str(self._reference_pi)

        match_count = 0
        for c1, c2 in zip(computed_str, reference_str):
            if c1 == c2:
                match_count += 1
            else:
                break

        # Subtract 2 to account for "3." at the start
        return match_count - 2

    def format_result(self, result: PiComputationResult, show_digits: int = 100) -> str:
        """
        Format the computation result for display.

        Args:
            result: PiComputationResult to format
            show_digits: Number of digits to display in the formatted string

        Returns:
            Formatted string with computation results
        """
        # Detect if we're in a Docker or non-interactive environment
        is_docker = os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER") == "true"
        is_non_interactive = not sys.stdout.isatty() or is_docker

        # Format the π value string
        pi_str = str(result.value)[: show_digits + 2]  # +2 for "3."

        # Basic information that's always included
        info = [
            f"Value (first {show_digits} digits): {pi_str}",
            f"Computation time: {result.computation_time:.2f} seconds",
            f"Requested precision: {result.precision} digits",
            f"Correct digits: {result.correct_digits}",
        ]

        # Add debug information if available
        if result.debug_info:
            info.append("\nDebug Information:")
            info.extend(f"{k}: {v}" for k, v in result.debug_info.items())

        # Use plain formatting for Docker/non-interactive environments
        if is_non_interactive:
            return "π Computation Results:\n" + "\n".join(info)

        # Use fancy formatting for interactive terminals
        return f"""π Computation Results:
{chr(9492) + chr(9472) * 2} """ + f"\n{chr(9474)}  ".join(
            info
        )
