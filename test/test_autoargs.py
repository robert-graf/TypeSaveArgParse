# Call 'python -m unittest' on this folder
# coverage run -m unittest
# coverage report
# coverage html
import random
import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from types import NoneType
from unittest.mock import patch

sys.path.append(str(Path(__file__).parent.parent.parent / "TypeSaveArgParse"))

from TypeSaveArgParse import Class_to_ArgParse  # noqa: E402

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
    except ValueError:
        pass
    else:
        raise ValueError()


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

    # tuple with lenght checks
    # list
    # optional list
    # Enum
    # Save/Load
    # Sub-Objects
    # Json-support
    # yaml support


if __name__ == "__main__":
    unittest.main()

# @unittest.skipIf(condition, reason)
# with self.subTest(i=i):
