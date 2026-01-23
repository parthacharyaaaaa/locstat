from typing import Optional
from cloc.data_structures.typing import SupportsBuffer

__all__ = ("_parse_memoryview",
           "_parse_buffered_object")

def _parse_memoryview(mapped_space: SupportsBuffer,
                      singleline_symbol: Optional[bytes] = None,
                      multiline_start_symbol: Optional[bytes] = None,
                      multiline_end_symbol: Optional[bytes] = None,
                      minimum_characters: int = 0
                      ) -> tuple[int, int]: ...

def _parse_buffered_object(buffered_object: SupportsBuffer,
                           singleline_symbol: Optional[bytes] = None,
                           multiline_start_symbol: Optional[bytes] = None,
                           multiline_end_symbol: Optional[bytes] = None,
                           minimum_characters: int = 0
                           ) -> tuple[int, int]: ...