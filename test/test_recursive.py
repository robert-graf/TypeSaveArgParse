# Call 'python -m unittest' on this folder
# coverage run -m unittest
# coverage report
# coverage html
import platform
import random
import sys
import unittest
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional
from unittest.mock import patch

import configargparse as argparse

sys.path.append(str(Path(__file__).parent.parent.parent / "TypeSaveArgParse"))

from TypeSaveArgParse import Class_to_ArgParse

DEFAULT_STR = str(random.randint(0, 1000))
DEFAULT_INT = random.randint(-1000, 1000)
DEFAULT_FLOAT = random.random()
py_version = int(platform.python_version().split(".")[1])


class Dummy_Enum(Enum):
    ONE = auto()
    SECOND = auto()
    THIRD = auto()


if py_version <= 9:

    @dataclass
    class BASE_CASES(Class_to_ArgParse):  # type: ignore
        """
        Class representing base cases for argument parsing.

        Attributes:
            x (str): String attribute with default value DEFAULT_STR.
            y (int): Integer attribute with default value DEFAULT_INT.
            f (float): Float attribute with default value DEFAULT_FLOAT.
            z (Optional[int]): Optional integer attribute.
            p (Optional[Path]): Optional Path attribute.
            l_s (List[str]): List of strings.
            l_i (List[int]): List of integers with default value [1, 2, 3].
            tup (Tuple[str, ...]): Tuple of strings.
            set_ (Set[str]): Set of strings.
        """

        x: str = DEFAULT_STR
        y: int = DEFAULT_INT
        f: float = DEFAULT_FLOAT
        z: Optional[int] = None
        p: Optional[Path] = None
        l_s: list[str] = field(default_factory=list)
        l_i: list[int] = field(default_factory=lambda: [1, 2, 3])
        tup: tuple[str, ...] = field(default_factory=tuple)
        set_: set[str] = field(default_factory=set)

    @dataclass
    class ENUM_CASES(Class_to_ArgParse):  # type: ignore
        """
        Class representing enum cases for argument parsing.

        Attributes:
            enu (Dummy_Enum): Enum attribute with default value Dummy_Enum.ONE.
            enu_list (Optional[List[Dummy_Enum]]): Optional list of enum instances.
            enu_list2 (List[Dummy_Enum]): List of enum instances.
        """

        enu: Dummy_Enum = Dummy_Enum.ONE
        enu_list: Optional[list[Dummy_Enum]] = None
        enu_list2: list[Dummy_Enum] = field(default_factory=list)


else:

    @dataclass
    class BASE_CASES(Class_to_ArgParse):
        """
        Class representing base cases for argument parsing.

        Attributes:
            x (str): String attribute with default value DEFAULT_STR.
            y (int): Integer attribute with default value DEFAULT_INT.
            f (float): Float attribute with default value DEFAULT_FLOAT.
            z (Optional[int]): Optional integer attribute.
            p (Optional[Path]): Optional Path attribute.
            l_s (List[str]): List of strings.
            l_i (List[int]): List of integers with default value [1, 2, 3].
            tup (Tuple[str, ...]): Tuple of strings.
            set_ (Set[str]): Set of strings.
        """

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
    class ENUM_CASES(Class_to_ArgParse):
        """
        Class representing enum cases for argument parsing.

        Attributes:
            enu (Dummy_Enum): Enum attribute with default value Dummy_Enum.ONE.
            enu_list (Optional[List[Dummy_Enum]]): Optional list of enum instances.
            enu_list2 (List[Dummy_Enum]): List of enum instances.
        """

        enu: Dummy_Enum = Dummy_Enum.ONE
        enu_list: list[Dummy_Enum] | None = None
        enu_list2: list[Dummy_Enum] = field(default_factory=list)


@dataclass
class RRR(Class_to_ArgParse):
    """
    Class representing RRR for argument parsing.

    Attributes:
        i (int): Integer attribute with default value 9.
    """

    i: int = 9


@dataclass
class TUP_CASES(Class_to_ArgParse):
    """
    Class representing tuple cases for argument parsing.

    Attributes:
        r (RRR): Instance of RRR class.
        tup (Tuple[int, ...]): Tuple of integers.
        tup1 (Tuple[int]): Singleton tuple of integers.
        tup2 (Tuple[int, int]): Tuple of two integers.
        tup3 (Tuple[int, int, int]): Tuple of three integers.
        tup4 (Tuple[int, int, int, int]): Tuple of four integers.
    """

    r: RRR
    tup: tuple[int, ...] = field(default_factory=tuple)
    tup1: tuple[int] = field(default_factory=tuple)
    tup2: tuple[int, int] = field(default_factory=tuple)
    tup3: tuple[int, int, int] = field(default_factory=tuple)
    tup4: tuple[int, int, int, int] = field(default_factory=tuple)


@dataclass()
class REC(Class_to_ArgParse):
    """
    Class representing REC for argument parsing.

    Attributes:
        bc (BASE_CASES): Instance of BASE_CASES class.
        tc (TUP_CASES): Instance of TUP_CASES class.
        ec (ENUM_CASES): Instance of ENUM_CASES class.
    """

    bc: BASE_CASES
    tc: TUP_CASES
    ec: ENUM_CASES


def assert_(value, x, type_):
    assert value == x, (value, x)
    assert isinstance(value, type_), (value, type_)


def err(idx):
    raise ValueError(idx)


def fetch_exit(args: Optional[list[str]] = None, fun=lambda: BASE_CASES().get_opt()):
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
        with patch("sys.argv", [__file__, "--tc.r.i", "8"]):
            opt = REC.get_opt()
            assert_(opt.tc.r.i, 8, int)

    def test_native2(self):
        with TemporaryDirectory() as a:
            file = Path(a, "test.yaml")
            org = REC(BASE_CASES(), TUP_CASES(RRR()), ENUM_CASES())
            org.save_config(file)
            with patch("sys.argv", [__file__, "--config", str(file)]):
                opt = REC.get_opt()
            assert opt == org, (opt, org)

    def test_native(self):
        with TemporaryDirectory() as a:
            file = Path(a, "test.yaml")
            org = REC(
                BASE_CASES(
                    "oli",
                    89,
                    0.1,
                    z=9,
                    p=Path("/my/hopes/and/dreams/"),
                    l_s=["empty"],
                    l_i=[1, 1, 1, 1, 1, 1],
                    tup=("hearth",),
                    set_={"functional", "paradigms"},
                ),
                TUP_CASES(RRR(5)),
                ENUM_CASES(),
            )
            org.save_config(file)
            with patch("sys.argv", [__file__, "--config", str(file)]):
                opt = REC.get_opt()
            assert opt == org, (opt, org)

    def test_native3(self):
        with TemporaryDirectory() as a:
            file = Path(a, "test3.yaml")
            org = REC(
                BASE_CASES("oli", 89, 0.1, z=9, p=Path("/my/hopes/and/dreams/"), l_s=[], l_i=[88], tup=(), set_=set()),
                TUP_CASES(RRR(5), tup=(1, 1, 1, 1, 1, 1), tup1=(1,), tup2=(1, 2), tup3=(1, 2, 3)),
                ENUM_CASES(),
            )
            org.save_config(file)
            with patch("sys.argv", [__file__, "--config", str(file)]):
                opt = REC.get_opt()
            assert opt == org, (opt, org)


# TODO Loop detection
if __name__ == "__main__":
    opt = REC.get_opt()
    # unittest.main()
    # print(opt)
# @unittest.skipIf(condition, reason)
# with self.subTest(i=i):
