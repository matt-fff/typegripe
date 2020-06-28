import ast
import pathlib
from dataclasses import dataclass
from enum import Enum, unique
from typing import List, Tuple, Optional

from loguru import logger


@dataclass
class Config:
    warn_on_unimplemented: bool = True
    python_version: Tuple[int, int] = (3, 8)


@unique
class WarnCode(Enum):
    UNTYPED_ARG = "untyped-arg"


@dataclass
class TypeWarning:
    code: WarnCode
    description: str
    line_num: int
    name: Optional[str]

    def __eq__(self, other):
        if not isinstance(other, TypeWarning):
            return False

        return (
            self.code == other.code
            and self.line_num == other.line_num
            and self.name == other.name
        )


config = Config()


def check_file(path: pathlib.Path) -> List[TypeWarning]:
    with path.open("r") as source_file:
        source = "\n".join(source_file.readlines())
        code = ast.parse(
            source,
            filename=path.name,
            type_comments=True,
            feature_version=config.python_version,
        )

        warnings = []
        for entry in code.body:
            warnings.extend(check_ast_object(entry))

    return warnings


def check_ast_object(obj) -> List[TypeWarning]:
    # TODO consider the effects of very deep recursion
    sub_objs = []
    warnings = []
    if isinstance(obj, ast.FunctionDef):
        sub_objs = [
            obj.args,
            obj.body,
            obj.returns,
        ]
    elif isinstance(obj, ast.arguments):
        sub_objs = [
            obj.args,
            obj.kwarg,
            obj.kwonlyargs,
            obj.posonlyargs,
        ]
    elif isinstance(obj, ast.arg):
        if obj.annotation is None:
            warnings.append(
                TypeWarning(
                    code=WarnCode.UNTYPED_ARG,
                    name=obj.arg,
                    line_num=obj.lineno,
                    description=f"argument '{obj.arg}' has no annotation",
                )
            )
    elif isinstance(obj, (set, list)):
        sub_objs = list(obj)
    elif config.warn_on_unimplemented:
        logger.warning(f"{type(obj)} is not yet supported.")

    for sub_obj in sub_objs:
        warnings.extend(check_ast_object(sub_obj))
    return warnings
