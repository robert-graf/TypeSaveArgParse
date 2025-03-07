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
from tempfile import TemporaryDirectory
from typing import Optional
from unittest.mock import patch

import configargparse as argparse

sys.path.append(str(Path(__file__).parent.parent.parent / "TypeSaveArgParse"))

from TypeSaveArgParse import Class_to_ArgParse

DEFAULT_STR = str(random.randint(0, 1000))
DEFAULT_INT = random.randint(-1000, 1000)
DEFAULT_FLOAT = random.random()


class Dummy_Enum(Enum):
    ONE = auto()
    SECOND = auto()
    THIRD = auto()


@dataclass
class BASE_CASES(Class_to_ArgParse):
    x: str = ""
    y: int = -1000000
    f: float = -0.3
    enum: Dummy_Enum = Dummy_Enum.ONE
    enum_tuple: tuple[Dummy_Enum, Dummy_Enum] = field(default_factory=lambda: (Dummy_Enum.ONE, Dummy_Enum.ONE))
    z: Optional[int] = None
    p: Optional[Path] = None
    l_s: list[str] = field(default_factory=lambda: ["Wam", "Bam"])
    l_i: list[int] = field(default_factory=lambda: [1, 2, 3])
    tup: tuple[str, ...] = field(default_factory=tuple)
    set_s: set[str] = field(default_factory=set)
    set_i: set[int] = field(default_factory=set)
    b: bool = False


class Test_save_load(unittest.TestCase):
    def test_native(self):
        # with TemporaryDirectory() as a:
        file = Path("test.yaml")
        org = BASE_CASES(
            DEFAULT_STR,
            DEFAULT_INT,
            DEFAULT_FLOAT,
            Dummy_Enum.SECOND,
            enum_tuple=(Dummy_Enum.THIRD, Dummy_Enum.ONE),
            z=99999,
            # p=Path(__file__).parent,
            l_s=["Buy", "more", "Bees"],
            l_i=[-1, -1, -4, -9],
            set_s={"1", "2"},
            set_i={1, 5},
            b=True,
        )
        org.save_config(file)
        with patch("sys.argv", [__file__, "--config", str(file)]):
            opt = BASE_CASES.get_opt()
        assert opt == org, (opt, org)

    def test_native2(self):
        with TemporaryDirectory() as a:
            file = Path(a, "test.yaml")
            org = BASE_CASES()
            org.save_config(file)
            with patch("sys.argv", [__file__, "--config", str(file)]):
                opt = BASE_CASES.get_opt()
            assert opt == org, (opt, org)


if __name__ == "__main__":
    unittest.main()

# @unittest.skipIf(condition, reason)
# with self.subTest(i=i):
