import os
from typing import Any, Literal, MutableMapping, Optional, Protocol, TypeAlias, Union

__all__ = ("OutputMapping", "LanguageMetadata", "OutputFunction")

OutputMapping: TypeAlias = MutableMapping[str, Union[MutableMapping[str, Any], int, str]]
LanguageMetadata: TypeAlias = tuple[Optional[bytes], Optional[bytes], Optional[bytes]]

class OutputFunction(Protocol):
    def __call__(self,
                 output_mapping: OutputMapping,
                 filepath: Union[str, os.PathLike[str], int],
                 mode: Literal["w+", "a"] = "w+") -> None:
        ...