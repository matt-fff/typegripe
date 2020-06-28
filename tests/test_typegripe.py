import pathlib
from typing import List

import pytest

from typegripe import __version__, check

FIXTURE_PATH = "./tests/file_fixtures"


def test_version():
    assert __version__ == "0.1.0"

@pytest.mark.skip(reason="Debugging")
@pytest.mark.parametrize("filename", ["valid_function.py", "empty.py",])
def test_valid_files(filename: str):
    assert [] == check.check_file(pathlib.Path(f"{FIXTURE_PATH}/{filename}"))


@pytest.mark.parametrize(
    "filename,expected_warnings",
    [
        (
            "function_missing_args.py",
            [
                check.Warning(
                    code=check.WarnCode.UNTYPED_ARG, description="", line_num=1, name='this'
                ),
                check.Warning(
                    code=check.WarnCode.UNTYPED_ARG, description="", line_num=1, name='thing'
                ),
            ],
        ),
    ],
)
def test_invalid_files(filename: str, expected_warnings: List[check.Warning]):
    assert expected_warnings == check.check_file(pathlib.Path(f"{FIXTURE_PATH}/{filename}"))

