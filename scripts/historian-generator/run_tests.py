# run_tests.py
import sys
import pytest

exit_code = pytest.main([
    "-v",
    "tests/test_historian_generator.py",
    "tests/test_alarm_log_generator.py",
    "tests/test_data_quality.py",
])
sys.exit(exit_code)
