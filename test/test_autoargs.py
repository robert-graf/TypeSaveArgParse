# Call 'python -m unittest' on this folder
# coverage run -m unittest
# coverage report
# coverage html
import argparse
import random
import sys
import unittest
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from types import NoneType
from unittest.mock import patch

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
class TUP_CASES(Class_to_ArgParse):
    tup: tuple[int, ...] = field(default_factory=tuple)
    tup1: tuple[int] = field(default_factory=tuple)
    tup2: tuple[int, int] = field(default_factory=tuple)
    tup3: tuple[int, int, int] = field(default_factory=tuple)
    tup4: tuple[int, int, int, int] = field(default_factory=tuple)


class Dummy_Enum(Enum):
    ONE = auto()
    SECOND = auto()
    THIRDs = auto()


@dataclass
class ENUM_CASES(Class_to_ArgParse):
    enu: Dummy_Enum = Dummy_Enum.ONE
    enu_list: list[Dummy_Enum] | None = None
    enu_list2: list[Dummy_Enum] = field(default_factory=list)


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
class Test_bids_file(unittest.TestCase):
    def test_native(self):
        with patch("sys.argv", [__file__]):
            opt = BASE_CASES().get_opt()
            assert_(opt.x, DEFAULT_STR, str)
            assert_(opt.y, DEFAULT_INT, int)
            assert_(opt.f, DEFAULT_FLOAT, float)
            assert_(opt.z, None, NoneType)
            assert_(opt.l_s, [], list)
            assert_(opt.l_i, [1, 2, 3], list)
            assert_(opt.set_, set(), set)
            assert_(opt.tup, (), tuple)
            assert_(opt.p, None, NoneType)
        value = "BananaBread"
        with patch("sys.argv", [__file__, "--x", "BananaBread"]):
            opt = BASE_CASES().get_opt()
            assert_(opt.x, value, str)
        with patch("sys.argv", [__file__, "--y", "999"]):
            opt = BASE_CASES().get_opt()
            assert_(opt.y, 999, int)
        with patch("sys.argv", [__file__, "--f", "0.3"]):
            opt = BASE_CASES().get_opt()
            assert_(opt.f, 0.3, float)
        with patch("sys.argv", [__file__, "--f", "3"]):
            opt = BASE_CASES().get_opt()
            assert_(opt.f, 3, float)
        with patch("sys.argv", [__file__, "--z", "3"]):
            opt = BASE_CASES().get_opt()
            assert_(opt.z, 3, int)
        with patch("sys.argv", [__file__, "--l_s", "a", "b", "c"]):
            opt = BASE_CASES().get_opt()
            assert_(opt.l_s, ["a", "b", "c"], list)
        with patch("sys.argv", [__file__, "--l_i", "42", "1337"]):
            opt = BASE_CASES().get_opt()
            assert_(opt.l_i, [42, 1337], list)
        with patch("sys.argv", [__file__, "--set", "1", "1", "2"]):
            opt = BASE_CASES().get_opt()
            assert_(opt.set_, {"1", "2"}, set)
        with patch("sys.argv", [__file__, "--tup", "1", "1", "3"]):
            opt = BASE_CASES().get_opt()
            assert_(opt.tup, ("1", "1", "3"), tuple)
        with patch("sys.argv", [__file__, "--p", __file__]):
            opt = BASE_CASES().get_opt()
            assert_(opt.p, Path(__file__), Path)

    def test_false_inputs(self):
        fetch_exit([__file__, "--z", "str instead of optional int"])
        fetch_exit([__file__, "--y", "str instead of int"])
        fetch_exit([__file__, "--f", "str instead of float"])

    def test_tuple(self):
        with patch("sys.argv", [__file__, "--tup", "1", "2", "3", "4"]):
            opt = TUP_CASES().get_opt()
            assert_(opt.tup, (1, 2, 3, 4), tuple)
        with patch("sys.argv", [__file__, "--tup", "-1", "4"]):
            opt = TUP_CASES().get_opt()
            assert_(opt.tup, (-1, 4), tuple)
        with patch("sys.argv", [__file__, "--tup1", "-1"]):
            opt = TUP_CASES().get_opt()
            assert_(opt.tup1, (-1,), tuple)
        with patch("sys.argv", [__file__, "--tup2", "-1", "3"]):
            opt = TUP_CASES().get_opt()
            assert_(opt.tup2, (-1, 3), tuple)
        with patch("sys.argv", [__file__, "--tup3", "-1", "3", "6"]):
            opt = TUP_CASES().get_opt()
            assert_(opt.tup3, (-1, 3, 6), tuple)
        with patch("sys.argv", [__file__, "--tup4", "-1", "3", "6", "-456"]):
            opt = TUP_CASES().get_opt()
            assert_(opt.tup4, (-1, 3, 6, -456), tuple)

    def test_false_tuple(self):
        def lam():
            return TUP_CASES().get_opt()

        # To lager
        fetch_exit([__file__, "--tup1", "1", "2"], lam)
        fetch_exit([__file__, "--tup2", "1", "2", "3"], lam)
        fetch_exit([__file__, "--tup3", "1", "2", "3", "4"], lam)
        fetch_exit([__file__, "--tup4", "1", "2", "3", "4", "5"], lam)
        fetch_exit([__file__, "--tup1"], lam)
        fetch_exit([__file__, "--tup2", "3"], lam)
        fetch_exit([__file__, "--tup3", "3", "4"], lam)
        fetch_exit([__file__, "--tup4", "3", "4", "5"], lam)

    def test_enum(self):
        with patch("sys.argv", [__file__, "--enu", Dummy_Enum.ONE.name]):
            opt = ENUM_CASES().get_opt()
            assert_(opt.enu, Dummy_Enum.ONE, Dummy_Enum)
        with patch("sys.argv", [__file__, "--enu", Dummy_Enum.THIRDs.name]):
            opt = ENUM_CASES().get_opt()
            assert_(opt.enu, Dummy_Enum.THIRDs, Dummy_Enum)
        with patch("sys.argv", [__file__, "--enu", Dummy_Enum.SECOND.name]):
            opt = ENUM_CASES().get_opt()
            assert_(opt.enu, Dummy_Enum.SECOND, Dummy_Enum)
        with patch("sys.argv", [__file__, "--enu_list", Dummy_Enum.SECOND.name, Dummy_Enum.ONE.name]):
            opt = ENUM_CASES().get_opt()
            assert_(opt.enu_list, [Dummy_Enum.SECOND, Dummy_Enum.ONE], list)
        with patch("sys.argv", [__file__, "--enu_list2", Dummy_Enum.SECOND.name, Dummy_Enum.ONE.name]):
            opt = ENUM_CASES().get_opt()
            assert_(opt.enu_list2, [Dummy_Enum.SECOND, Dummy_Enum.ONE], list)
        with patch("sys.argv", [__file__, "--enu_list2", Dummy_Enum.THIRDs.name]):
            opt = ENUM_CASES().get_opt()
            assert_(opt.enu_list2, [Dummy_Enum.THIRDs], list)

    def test_false_enum(self):
        def lam():
            return ENUM_CASES().get_opt()

        # To lager
        fetch_exit([__file__, "--enu", "FALSE TEXT"], lam)
        fetch_exit([__file__, "--enu_list", "FALSE TEXT"], lam)
        fetch_exit([__file__, "--enu_list2", "STILL FALSE TEXT"], lam)
        # TO MANY ARGS
        fetch_exit([__file__, "--enu", Dummy_Enum.SECOND.name, Dummy_Enum.ONE.name], lam)


# Save/Load
# Sub-Objects
# Json-support
# yaml support
# list
# optional list


if __name__ == "__main__":
    unittest.main()

# @unittest.skipIf(condition, reason)
# with self.subTest(i=i):
