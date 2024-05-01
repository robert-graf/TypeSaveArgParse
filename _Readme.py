from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path

from TypeSaveArgParse import Class_to_ArgParse


# We support Enums
class Dummy_Enum(Enum):
    ONE = auto()
    SECOND = auto()
    THIRD = auto()


# 1.  Make a data class that inherits from TypeSaveArgParse.Class_to_ArgParse
@dataclass
class BASE_CASES(Class_to_ArgParse):
    x: str = "your api key now on GitHub"
    y: int = -1000000
    f: float = -0.3
    int_with_optional: int | None = None
    p: Path | None = None
    enum: Dummy_Enum = Dummy_Enum.ONE
    enum_tuple: tuple[Dummy_Enum, Dummy_Enum] = field(default_factory=lambda: (Dummy_Enum.ONE, Dummy_Enum.ONE))
    list_str: list[str] = field(default_factory=lambda: ["Wam", "Bam"])
    list_int: list[int] = field(default_factory=lambda: [1, 2, 3])
    tuple_any_len: tuple[str, ...] = field(default_factory=tuple)
    tuple_with_fixed_lenght: tuple[str, str] = field(default_factory=lambda: ("A", "B"))
    set_s: set[str] = field(default_factory=set)
    set_i: set[int] = field(default_factory=set)
    b: bool = False


# 2. Call the get_opt method to start ArgParse and get the filled out Object

base_cases = BASE_CASES.get_opt()

# With -h you will see all options
# With --config [PATH-TO-CONFIG] you can add a Config-file that overrides default but not set arguments. (For more info see the configargparse package)

# 3. You can save the current status of your config with save_config
base_cases.save_config("myConfig.yaml")
