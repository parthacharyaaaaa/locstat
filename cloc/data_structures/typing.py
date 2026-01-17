import os
from typing import Any, Literal, MutableMapping, Optional, Protocol, TypeAlias, TypeVar, Union

__all__ = ("OutputMapping", "LanguageMetadata", "OutputFunction", "SupportsMembershipChecks")

OutputMapping: TypeAlias = MutableMapping[str, Union[MutableMapping[str, Any], int, str]]
LanguageMetadata: TypeAlias = tuple[Optional[bytes], Optional[bytes], Optional[bytes]]

class OutputFunction(Protocol):
    def __call__(self,
                 output_mapping: OutputMapping,
                 filepath: Union[str, os.PathLike[str], int],
                 mode: Literal["w+", "a"] = "w+") -> None:
        ...

T = TypeVar("T", covariant=True)
class SupportsMembershipChecks(Protocol[T]):
    def __contains__(self, o: object, /) -> bool: ...