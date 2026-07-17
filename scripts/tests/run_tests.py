# run_tests.py
"""Run all unit tests for historian and alarm log generation."""
import sys
import pytest

exit_code = pytest.main([
    "-v",
    "test_historian_generator.py",
    "test_alarm_log_generator.py",
    "test_data_quality.py",
])
sys.exit(exit_code)
