# Call 'python -m unittest' on this folder
# coverage run -m unittest
# coverage report
# coverage html
import random
import sys
import unittest
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from types import NoneType
from unittest.mock import patch

import configargparse as argparse

sys.path.append(str(Path(__file__).parent.parent.parent / "TypeSaveArgParse"))

from TypeSaveArgParse import Class_to_ArgParse

DEFAULT_STR = str(random.randint(0, 1000))
DEFAULT_INT = random.randint(-1000, 1000)
DEFAULT_FLOAT = random.random()


@dataclass
class BASE_CASES(Class_to_ArgParse):
    x: str = DEFAULT_STR
    y: int = DEFAULT_INT
    f: float = DEFAULT_FLOAT
    z: int | None = None
    p: Path | None = None
    l_s: list[str] = field(default_factory=list)
    l_i: list[int] = field(default_factory=lambda: [1, 2, 3])
    tup: tuple[str, ...] = field(default_factory=tuple)
    set_: set[str] = field(default_factory=set)


@dataclass
class RRR(Class_to_ArgParse):
    i: int = 9


@dataclass
class TUP_CASES(Class_to_ArgParse):
    r: RRR
    tup: tuple[int, ...] = field(default_factory=tuple)
    tup1: tuple[int] = field(default_factory=tuple)
    tup2: tuple[int, int] = field(default_factory=tuple)
    tup3: tuple[int, int, int] = field(default_factory=tuple)
    tup4: tuple[int, int, int, int] = field(default_factory=tuple)


class Dummy_Enum(Enum):
    ONE = auto()
    SECOND = auto()
    THIRD = auto()


@dataclass
class ENUM_CASES(Class_to_ArgParse):
    enu: Dummy_Enum = Dummy_Enum.ONE
    enu_list: list[Dummy_Enum] | None = None
    enu_list2: list[Dummy_Enum] = field(default_factory=list)


@dataclass()
class REC(Class_to_ArgParse):
    bc: BASE_CASES
    tc: TUP_CASES
    ec: ENUM_CASES


def assert_(value, x, type_):
    assert value == x, (value, x)
    assert isinstance(value, type_), (value, type_)


def err(idx):
    raise ValueError(idx)


def fetch_exit(args: list | None = None, fun=lambda: BASE_CASES().get_opt()):
    if args is None:
        args = [__file__, "--z", "C. CLark"]
    try:
        with patch("sys.argv", args), patch("sys.exit", err):
            fun()
    except (ValueError, argparse.ArgumentTypeError):
        pass
    else:
        raise ValueError()


# https://docs.python.org/dev/library/argparse.html#sub-commands
class Test_autoargs(unittest.TestCase):
    # def test_false_inputs(self):
    #    fetch_exit([__file__, "--z", "str instead of optional int"])
    #    fetch_exit([__file__, "--y", "str instead of int"])
    #    fetch_exit([__file__, "--f", "str instead of float"])

    def test_tuple(self):
        with patch("sys.argv", [__file__]):
            opt = REC.get_opt()
            print(opt)
            # opt.save_config("myConfig.yaml")
            # assert_(opt.tup, (1, 2, 3, 4), tuple)


# TODO Loop detection
if __name__ == "__main__":
    opt = REC.get_opt()
    # unittest.main()
    print(opt)
# @unittest.skipIf(condition, reason)
# with self.subTest(i=i):
