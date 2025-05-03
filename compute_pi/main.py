"""Command-line interface for π calculation."""

import argparse
import sys
from typing import Optional
import logging

from tqdm.auto import tqdm

from compute_pi import PiCalculator
from .logger import logger, setup_logger


def create_progress_bar(total: int) -> tqdm:
    """Create a progress bar for the calculation."""
    return tqdm(
        total=100,
        desc="Computing π",
        unit="%",
        ncols=80,
        bar_format="{l_bar}{bar}| {n_fmt}%/{total_fmt}% [{elapsed}<{remaining}]"
    )


def progress_callback(progress: float, pbar: Optional[tqdm] = None) -> None:
    """Update progress bar with current progress."""
    if pbar:
        pbar.n = int(progress * 100)
        pbar.refresh()


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Calculate π to a specified precision using the Chudnovsky algorithm"
    )
    parser.add_argument(
        "-p", "--precision",
        type=int,
        default=1000,
        help="Number of decimal places to compute (default: 1000)"
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar"
    )
    parser.add_argument(
        "--show-digits",
        type=int,
        default=100,
        help="Number of digits to display in output (default: 100)"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path (optional)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    try:
        # Configure logger
        log_level = logging.DEBUG if args.verbose else logging.INFO
        setup_logger(
            level=log_level,
            log_file=args.log_file,
            use_tqdm=not args.no_progress
        )

        calculator = PiCalculator(precision=args.precision)
        
        if args.no_progress:
            result = calculator.compute_pi()
        else:
            with create_progress_bar(100) as pbar:
                result = calculator.compute_pi(
                    progress_callback=lambda p: progress_callback(p, pbar)
                )

        print(calculator.format_result(result, show_digits=args.show_digits))
        return 0

    except ValueError as e:
        logger.error(str(e))
        return 1
    except KeyboardInterrupt:
        logger.info("\nComputation interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if args.verbose:
            logger.exception("Detailed error information:")
        return 2


if __name__ == "__main__":
    sys.exit(main())
