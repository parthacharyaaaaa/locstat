from pathlib import Path
from typing import Iterable

from locstat.parsing.extensions._parsing import (
    _parse_file_vm_map,
    _parse_file_no_chunk,
    _parse_file,
)
from locstat.data_structures.typing import (
    FileLineData,
    FileParsingFunction,
    LanguageMetadata,
)

from tests.fixtures import mock_dir
from tests.constants import UNIX_NEWLINE, WIN_NEWLINE


def _test_helper_run_all_parsers(
    file: Path,
    comment_data: LanguageMetadata,
    expected_output: FileLineData,
    minimum_characters: int = 1,
    parsers: Iterable[FileParsingFunction] = (
        _parse_file,
        _parse_file_no_chunk,
        _parse_file_vm_map,
    ),
):
    results: dict[FileParsingFunction, FileLineData] = {
        parser: parser(str(file), *comment_data, minimum_characters)
        for parser in parsers
    }

    expected_total, expected_loc, expected_commented, expected_blank = expected_output

    failures: list[str] = [
        ", ".join(
            (
                parser.__qualname__,
                f"Total: Expected = {expected_total}, Observed = {total}",
                f"LOC: Expected = {expected_loc}, Observed = {loc}",
                f"Commented: Expected = {expected_commented}, Observed = {commented}",
                f"Blank: Expected = {expected_blank}, Observed = {blank}",
            )
        )
        for parser, (total, loc, commented, blank) in results.items()
        if (total, loc, commented, blank) != expected_output
    ]
    assert not failures, "\n".join(failures)


def test_parsing_singleline_only(mock_dir) -> None:
    lines: list[str] = [
        "# This is a comment",
        "def foo(arg: int) -> None:",
        "\tos.remove('/')",
        "\t# Here's another comment",
        "",
        "\treturn None",
    ]

    expected_total, expected_loc, expected_commented, expected_blank = (
        len(lines),
        3,
        2,
        1,
    )
    mock_file: Path = mock_dir / "_mock_file.py"
    mock_file.touch()

    mock_file.write_text(UNIX_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"#", None, None),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )

    mock_file.write_text(WIN_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"#", None, None),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )


def test_parsing_multiline_only(mock_dir) -> None:
    lines: list[str] = [
        "/* This is a comment",
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
        "}",
    ]

    expected_total, expected_loc, expected_commented, expected_blank = (
        len(lines),
        6,
        8,
        1,
    )
    mock_file: Path = mock_dir / "_mock_file.c"
    mock_file.touch()

    mock_file.write_text(UNIX_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"//", b"/*", b"*/"),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )

    mock_file.write_text(WIN_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"//", b"/*", b"*/"),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )


def test_parsing_nested(mock_dir) -> None:
    lines: list[str] = [
        "// Nested comments!",
        "/* Here's a multiline block",
        "//",
        "// */",
        "// The above line should end the commmented block",
        "int main(){return 0;}",
    ]

    expected_total, expected_loc, expected_commented, expected_blank = (
        len(lines),
        1,
        5,
        0,
    )
    mock_file: Path = mock_dir / "_mock_file.c"
    mock_file.touch()

    mock_file.write_text(UNIX_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"//", b"/*", b"*/"),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )

    mock_file.write_text(WIN_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"//", b"/*", b"*/"),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )


def test_parsing_inline(mock_dir) -> None:
    lines: list[str] = ["int main(){", "return /* Here's Johnny! */ 0;", "}"]

    expected_total, expected_loc, expected_commented, expected_blank = (
        len(lines),
        3,
        0,
        0,
    )
    mock_file: Path = mock_dir / "_mock_file.c"
    mock_file.touch()

    mock_file.write_text(UNIX_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"//", b"/*", b"*/"),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )

    mock_file.write_text(WIN_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"//", b"/*", b"*/"),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )


def test_parsing_single_inline(mock_dir) -> None:
    lines: list[str] = ["int main(){", "return 0;", "} // Inline singleline comment!"]

    expected_total, expected_loc, expected_commented, expected_blank = (
        len(lines),
        2,
        0,
        1,
    )
    mock_file: Path = mock_dir / "_mock_file.c"
    mock_file.touch()

    mock_file.write_text(UNIX_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"//", b"/*", b"*/"),
        (expected_total, expected_loc, expected_commented, expected_blank),
        minimum_characters=2,
    )

    mock_file.write_text(WIN_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"//", b"/*", b"*/"),
        (expected_total, expected_loc, expected_commented, expected_blank),
        minimum_characters=2,
    )


def test_parsing_split_inline(mock_dir) -> None:
    lines: list[str] = ["int x = /* Surprise! */ 1;"]

    expected_total, expected_loc, expected_commented, expected_blank = (
        len(lines),
        1,
        0,
        0,
    )
    mock_file: Path = mock_dir / "_mock_file.c"
    mock_file.touch()

    mock_file.write_text(UNIX_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"//", b"/*", b"*/"),
        (expected_total, expected_loc, expected_commented, expected_blank),
        minimum_characters=7,
    )

    mock_file.write_text(WIN_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"//", b"/*", b"*/"),
        (expected_total, expected_loc, expected_commented, expected_blank),
        minimum_characters=7,
    )


def test_asymmetric_multiline_symbols(mock_dir) -> None:
    lines: list[str] = ["<!-- Start", "Continuation", "End -->"]

    expected_total, expected_loc, expected_commented, expected_blank = (
        len(lines),
        0,
        3,
        0,
    )

    mock_file: Path = mock_dir / "_mock_file.html"
    mock_file.touch()

    mock_file.write_text(UNIX_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (None, b"<!--", b"-->"),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )

    mock_file.write_text(WIN_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (None, b"<!--", b"-->"),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )


def test_incorrect_comment(mock_dir) -> None:
    lines: list[str] = [
        "// This is a comment",
        "/ / But this isn't!",
        "/ * Is also not a comment",
        "/* But this starts a block",
        "* / this doesn't end the block",
        "but this does! */",
    ]

    expected_total, expected_loc, expected_commented, expected_blank = (
        len(lines),
        2,
        4,
        0,
    )
    mock_file: Path = mock_dir / "_mock_file.c"
    mock_file.touch()

    mock_file.write_text(UNIX_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"//", b"/*", b"*/"),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )

    mock_file.write_text(WIN_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"//", b"/*", b"*/"),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )


def test_min_chars_0(mock_dir) -> None:
    lines: list[str] = [" " for _ in range(5)]
    expected_total = expected_loc = len(lines)
    expected_commented = expected_blank = 0
    mock_file: Path = mock_dir / "_mock_file.py"
    mock_file.touch()

    mock_file.write_text(UNIX_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"#", None, None),
        (expected_total, expected_loc, expected_commented, expected_blank),
        minimum_characters=0,
    )

    mock_file.write_text(WIN_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"#", None, None),
        (expected_total, expected_loc, expected_commented, expected_blank),
        minimum_characters=0,
    )


def test_continuation_bytes(mock_dir) -> None:
    lines: list[str] = [
        "def main() -> None:",
        "\tprint('Watch out!')",
        "\t🐍",
        "\t🐍🐍",
    ]

    expected_total, expected_loc, expected_commented, expected_blank = (
        len(lines),
        3,
        0,
        1,
    )
    mock_file: Path = mock_dir / "_mock_file.py"
    mock_file.touch()
    mock_file.write_text("\n".join(lines))

    mock_file.write_text(UNIX_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"#", None, None),
        (expected_total, expected_loc, expected_commented, expected_blank),
        minimum_characters=2,
    )

    mock_file.write_text(WIN_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"#", None, None),
        (expected_total, expected_loc, expected_commented, expected_blank),
        minimum_characters=2,
    )


def test_missing_newline(mock_dir) -> None:
    lines: list[str] = ["def main() -> None: ..."]
    expected_total, expected_loc, expected_commented, expected_blank = 1, 1, 0, 0

    mock_file: Path = mock_dir / "_mock_file.py"
    mock_file.touch()
    mock_file.write_text("\n".join(lines))

    mock_file.write_text(UNIX_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"#", None, None),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )

    mock_file.write_text(WIN_NEWLINE.join(lines))
    _test_helper_run_all_parsers(
        mock_file,
        (b"#", None, None),
        (expected_total, expected_loc, expected_commented, expected_blank),
    )
