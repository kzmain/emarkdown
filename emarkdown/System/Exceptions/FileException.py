class InputFileTypeNotCorrectError(Exception):
    """Raised when the input file type is not accepted"""


class OutputFileTypeNotCorrectError(Exception):
    """Raised when the Output file type is not accepted"""


class FileAccessModeNotCorrectError(Exception):
    """Raised when the input/output file's access mode is not accepted"""
