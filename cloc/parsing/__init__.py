'''Subpackage to encapsulate parsing logic'''

from .directory import (parse_directory,
                        parse_directory_verbose)
from .file import (parse_buffered_file,
                   parse_complete_buffer,
                   parse_file_mmap)

__all__ = ("parse_buffered_file",
           "parse_complete_buffer",
           "parse_file_mmap",
           "parse_directory",
           "parse_directory_verbose")