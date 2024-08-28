from enum import Enum
from typing import Any, List, Optional, TypedDict


class TopCoderDivision(TypedDict):
    division_id: int
    levels: List[int]


class TopCoderScraperConfig(TypedDict):
    divisions: Optional[List[TopCoderDivision]]
    generate_tests: Optional[bool]
    url: Optional[str]
    limit: Optional[int]
    page: Optional[int]


class TopCoderType(Enum):
    STRING = 1
    STRING_LIST = 2
    INT = 3
    INT_LIST = 4
    FLOAT = 5
    FLOAT_LIST = 6
    BOOL = 7
    BOOL_LIST = 8

    @classmethod
    def from_string(cls, str_type: str) -> "TopCoderType":
        str_type_sanitized = str_type.lower().strip()
        if str_type_sanitized == "string":
            return TopCoderType.STRING
        if str_type_sanitized == "string[]":
            return TopCoderType.STRING_LIST
        if "int[]" in str_type_sanitized:
            return TopCoderType.INT_LIST
        if "int" in str_type_sanitized:
            return TopCoderType.INT
        if "float[]" in str_type_sanitized:
            return TopCoderType.FLOAT_LIST
        if "float" in str_type_sanitized:
            return TopCoderType.FLOAT
        if str_type_sanitized == "bool":
            return TopCoderType.BOOL
        if str_type_sanitized == "bool[]":
            return TopCoderType.BOOL_LIST
        if "double[]" in str_type_sanitized:
            return TopCoderType.FLOAT
        if "double" in str_type_sanitized:
            return TopCoderType.FLOAT
        if "long[]" in str_type_sanitized:
            return TopCoderType.INT
        if "long" in str_type_sanitized:
            return TopCoderType.INT
        if "char" in str_type_sanitized:
            return TopCoderType.STRING
        if "char[]" in str_type_sanitized:
            return TopCoderType.STRING_LIST

    def __str__(self):
        if self == TopCoderType.STRING:
            return "str"
        if self == TopCoderType.STRING_LIST:
            return "List[str]"
        if self == TopCoderType.INT:
            return "int"
        if self == TopCoderType.INT_LIST:
            return "List[int]"
        if self == TopCoderType.FLOAT:
            return "float"
        if self == TopCoderType.FLOAT_LIST:
            return "List[float]"
        if self == TopCoderType.BOOL:
            return "bool"
        if self == TopCoderType.BOOL_LIST:
            return "List[bool]"


TOPCODER_LIST_TYPES = [TopCoderType.STRING_LIST, TopCoderType.INT_LIST, TopCoderType.FLOAT_LIST, TopCoderType.BOOL_LIST]


class TopCoderProblemParameter(TypedDict):
    name: str
    type: TopCoderType


class TopCoderProblemTestCase(TypedDict):
    inputs: List
    output: Any


class TopCoderProblem(TypedDict):
    id: str
    description: str
    func_name: str
    parameters: List[TopCoderProblemParameter]
    return_type: TopCoderType
    test_cases: List[TopCoderProblemTestCase]