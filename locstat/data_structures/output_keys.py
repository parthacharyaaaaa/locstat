from enum import StrEnum

__all__ = ("OutputKeys",)


class OutputKeys(StrEnum):
    GENERAL = "General"
    TOTAL = "TOTAL"
    LOC = "LOC"
    COMMENTED = "Comments"
    BLANK = "Blank"

    FILES = "Files"
    SUBDIRECTORIES = "SUBDIRECTORIES"
