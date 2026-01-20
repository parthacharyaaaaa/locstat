'''Unit tests for function construction logic'''

from typing import Callable
from cloc.utilities.core import construct_directory_filter

def test_directory_exclusion_filter():
    dummy_directories: list[str] = ["foo", "bar", "foo/bar", "foo/foo/bar"]
    excluded_directories: set[str] = {"bar", "foo/bar"}
    directory_filter: Callable[[str], bool] = construct_directory_filter(excluded_directories,
                                                                         exclude=True)
    for directory in dummy_directories:
        result: bool = directory_filter(directory)
        # Exclusion test
        if directory in excluded_directories:
            assert not result, \
            f"Directory '{directory}' incorrectly included by constructed filter"

        # !Excluded directories should pass
        else:
            assert result, \
            f"Directory '{directory}' incorrectly excluded by constructed filter"

def test_directory_inclusion_filter():
    dummy_directories: list[str] = ["foo", "bar", "foo/bar", "foo/foo/bar"]
    included_directories: set[str] = {"bar", "foo/bar"}
    directory_filter: Callable[[str], bool] = construct_directory_filter(included_directories,
                                                                         include=True)
    for directory in dummy_directories:
        result: bool = directory_filter(directory)
        # Inclusion test
        if directory in included_directories:
            assert result, \
            f"Directory '{directory}' incorrectly excluded by constructed filter"

        # !Included directories should not pass
        else:
            assert not result, \
            f"Directory '{directory}' incorrectly included by constructed filter"