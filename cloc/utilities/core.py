from typing import Callable, Literal

from cloc.data_structures.parse_modes import ParseMode
from cloc.data_structures.typing import SupportsMembershipChecks, FileParsingFunction
from cloc.parsing.file import parse_file_mmap, parse_buffered_file, parse_complete_buffer

__all__ = ("construct_file_filter",
           "construct_directory_filter",
           "derive_file_parser")

def construct_file_filter(extension_set: SupportsMembershipChecks[str],
                          file_set: SupportsMembershipChecks[str],
                          include_file: bool = False,
                          exclude_file: bool = False,
                          include_type: bool = False,
                          exclude_type: bool = False) -> Callable[[str], bool]:
    file_filter: Callable[[str], bool] = lambda file : True
    if include_file:
        if include_type:
            file_filter = lambda file : ((file.rsplit(".", 1)[-1] in extension_set)
                                            or file in file_set)
        elif exclude_type:
            file_filter = lambda file : ((file.rsplit(".", 1)[-1] not in extension_set)
                                            or file in file_set)
        else:
            file_filter = lambda file : file in file_set
    elif exclude_file:
        if include_type:
            file_filter = lambda file : ((file.rsplit(".", 1)[-1] in extension_set)
                                            or file not in file_set)
        elif exclude_type:
            file_filter = lambda file : ((file.rsplit(".", 1)[-1] not in extension_set)
                                            or file not in file_set)
        else:
            file_filter = lambda file : file not in file_set
    
    return file_filter

def construct_directory_filter(directories: SupportsMembershipChecks[str],
                               exclude: bool = False,
                               include: bool = False) -> Callable[[str], bool]:
    if exclude:
        return lambda directory : directory not in directories
    elif include:
        return lambda directory : directory in directories
    return lambda directory : True

def derive_file_parser(option: ParseMode) -> FileParsingFunction:
    if option == ParseMode.MMAP:
        return parse_file_mmap
    elif option == ParseMode.COMPLETE:
        return parse_complete_buffer
    return parse_buffered_file
    