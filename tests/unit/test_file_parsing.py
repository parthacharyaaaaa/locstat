from pathlib import Path

from cloc.parsing.extensions._parsing import (_parse_file_vm_map,
                                              _parse_file_no_chunk,
                                              _parse_file)
from cloc.data_structures.typing import FileParsingFunction
from tests.fixtures import mock_dir

def test_parsing_singleline_only(mock_dir) -> None:
    lines: list[str] = ["# This is a comment",
                        "def foo(arg: int) -> None:",
                        "\tos.remove('/')",
                        "\t# Here's another comment",
                        "",
                        "\treturn None"]

    expected_total, expected_loc = len(lines), 3

    mock_file: Path = mock_dir / "_mock_file.py"
    mock_file.touch()
    mock_file.write_text("\n".join(lines))

    parsers: list[FileParsingFunction] = [_parse_file, _parse_file_no_chunk, _parse_file_vm_map]
    for parser in parsers:
        total, loc = parser(str(mock_file.resolve()),
                            b"#", None, None, 0)
        assert total == expected_total, \
        f"Expected to count {expected_total} total lines, {parser.__qualname__} counted {total} instead."

        assert loc == expected_loc, \
        f"Expected to count {expected_loc} LOC, {parser.__qualname__} counted {loc} instead."

def test_parsing_multiline_only(mock_dir) -> None:
    lines: list[str] = ["/* This is a comment",
                        "This is a continuation",
                        "This is a continuation",
                        "This is a continuation",
                        "All good things must come to an end */",
                        "",
                        "#include <stdlib.h>",
                        "int main(){",
                        "\tint x = 10;",
                        "\tbool y = false;",
                        "/* Look whos here again!",
                        "This is a continuation",
                        "Bye bye! */",
                        "return 0;",
                        "}"]

    expected_total, expected_loc = len(lines), 6

    mock_file: Path = mock_dir / "_mock_file.c"
    mock_file.touch()
    mock_file.write_text("\n".join(lines))

    parsers: list[FileParsingFunction] = [_parse_file, _parse_file_no_chunk, _parse_file_vm_map]
    for parser in parsers:
        total, loc = parser(str(mock_file.resolve()),
                            b"//", b"/*", b"*/", 0)
        assert total == expected_total, \
        f"Expected to count {expected_total} total lines, {parser.__qualname__} counted {total} instead."

        assert loc == expected_loc, \
        f"Expected to count {expected_loc} LOC, {parser.__qualname__} counted {loc} instead."