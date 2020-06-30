import ast
import pathlib
from dataclasses import dataclass
from enum import Enum, unique
from itertools import chain
from typing import List, Tuple, Optional, Iterable, Dict

from loguru import logger
from unsync import unsync

TYPE_COMMENT_NODES = (
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.Assign,
    ast.For,
    ast.AsyncFor,
    ast.With,
    ast.AsyncWith,
    ast.arg,
)
TYPE_ANNOTATION_NODES = (ast.AnnAssign, ast.arg)
TERMINATING_NODES = (type(None), ast.arg, ast.Return)


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


@unsync
async def sort_warnings(tasks) -> Dict[int, List[TypeWarning]]:
    warnings: Dict[int, List[TypeWarning]] = {}
    for task in tasks:
        for task_warning in await task:  # type: TypeWarning
            warnings.setdefault(task_warning.line_num, []).append(task_warning)

    return warnings


def check_file(path: pathlib.Path) -> Iterable[TypeWarning]:
    with path.open("r") as source_file:
        source = "\n".join(source_file.readlines())
        code = ast.parse(
            source,
            filename=path.name,
            type_comments=True,
            feature_version=config.python_version,
        )

        return list(check_ast_object(code).result())


def is_typed_object(obj) -> bool:
    # TODO handle type comments
    return isinstance(obj, TYPE_ANNOTATION_NODES)


@unsync
def get_warning(obj) -> List[TypeWarning]:
    return (
        [
            TypeWarning(
                # TODO decide what to do with different WarnCodes
                code=WarnCode.UNTYPED_ARG,
                name=obj.arg,
                line_num=obj.lineno,
                description=f"argument '{obj.arg}' has no annotation",
            )
        ]
        if obj.annotation is None
        else []
    )


@unsync
async def check_ast_object(obj) -> Iterable[TypeWarning]:
    sub_tasks = []
    if is_typed_object(obj):
        sub_tasks.append(get_warning(obj))

    if isinstance(obj, ast.Module):
        for entry in obj.body:
            sub_tasks.append(check_ast_object(entry))
    elif isinstance(obj, list):
        for entry in obj:
            sub_tasks.append(check_ast_object(entry))
    elif isinstance(obj, ast.FunctionDef):
        sub_tasks.append(check_ast_object(obj.args))
        sub_tasks.append(check_ast_object(obj.body))
        # TODO returns is just a name, so it needs to be processed alongside
        # the function itself.
        # sub_tasks.append(check_ast_object(obj.returns))
    elif isinstance(obj, ast.arguments):
        sub_tasks.append(check_ast_object(obj.args))
        sub_tasks.append(check_ast_object(obj.kwarg))
        sub_tasks.append(check_ast_object(obj.kwonlyargs))
        sub_tasks.append(check_ast_object(obj.posonlyargs))
    elif not isinstance(obj, TERMINATING_NODES):
        logger.debug(f"{type(obj)} is not yet supported.")

    return chain.from_iterable([await sub_task for sub_task in sub_tasks])
