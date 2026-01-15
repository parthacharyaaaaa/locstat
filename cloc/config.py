'''Python objects for storing config info'''
import orjson
from pathlib import Path
from types import SimpleNamespace, MappingProxyType
from typing import Final

__all__ = ("WORKING_DIRECTORY", "LANGUAGES", "DEFAULTS")

WORKING_DIRECTORY: Final[Path] = Path(__file__).parent

with open(WORKING_DIRECTORY / "languages.json", "rb") as lang:
    LANGUAGES: Final[MappingProxyType[str, dict[str, str]]] = MappingProxyType(orjson.loads(lang.read()))

with open(WORKING_DIRECTORY / "config.json", "rb") as config:
    DEFAULTS: SimpleNamespace = SimpleNamespace(**{flag: default
                                                   for flag, default
                                                   in orjson.loads(config.read())['defaults'].items()})