# TypeSaveArgParse

This package makes a data class to an ArgParse with ConfigArgParse as a backbone to load in or yaml files as a config file.

Basic Use

```Python
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path

from TypeSaveArgParse import Class_to_ArgParse


# We support Enums
class Dummy_Enum(Enum):
    ONE = auto()
    SECOND = auto()
    THIRD = auto()


# 1.  Make a data class that inherits from TypeSaveArgParse.Class_to_ArgParse
@dataclass
class BASE_CASES(Class_to_ArgParse):
    x: str = "Your API key now on GitHub"
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


# 2. Call the get_opt method to start ArgParse and get them filled out object.

base_cases = BASE_CASES.get_opt()

# With -h you will see all options
# With --config [PATH-TO-CONFIG], you can add a Config-file that overrides default but does not set arguments. (For more info, see the configargparse package)

# 3. You can save the current status of your config with save_config
base_cases.save_config("myConfig.yaml")
```

The resulting config looks like this:

```yaml
x: Your API key now on GitHub
y: -1000000
# int_with_optional: None # int | None
# p: None # pathlib.Path | None
f: -0.3
enum: ONE # <enum "Dummy_Enum"> Choices:["ONE", "SECOND", "THIRD"] - default [Dummy_Enum.ONE]
# Note: Tuple with a fixed size of 2
enum_tuple: [ONE, ONE] # <enum "Dummy_Enum"> Choices:["ONE", "SECOND", "THIRD"] 
list_str: [Wam, Bam]
# tuple_any_len: () # tuple[str, ...]
list_int: [1, 2, 3]
# set_s: set() # set[str]
# set_i: set() # set[int]
# Note: Tuple with a fixed size of 2
tuple_with_fixed_lenght: [A, B]
b: false # [True|False] - default [False]
```

Empty list/tuple/set and None can be set as a default and can be overridden. But you can not override values with an empty list or None. 

You can add other data classes. They will be always initialized from deepest nesting to lowest.  

# Help message

Help messages are pares from the doc string

```python
@dataclass
class BASE_CASES(Class_to_ArgParse):
    """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Morbi dapibus orci nec semper iaculis. In hac habitasse platea dictumst. Curabitur auctor tortor vel accumsan pulvinar. Proin malesuada sapien ut metus dignissim, non convallis lectus consectetur. Sed efficitur tellus vel nunc consequat, vel tristique velit ultrices. Curabitur tincidunt, nisi nec rhoncus consequat, felis erat dictum metus, ac gravida dui urna id metus. Phasellus in nulla eu purus suscipit posuere nec vel risus. Suspendisse ac lorem vitae arcu aliquet fringilla ac id libero. Nam sit amet sem et nulla sodales dapibus vel vel velit. Proin accumsan libero ut nunc ultrices, at mattis est malesuada. Nam sed lacinia urna. Vestibulum tristique ligula vel purus aliquet, vitae fermentum elit suscipit. Duis id risus a mauris suscipit lobortis. Curabitur suscipit lectus nec elit convallis, sed varius turpis venenatis. Nullam rhoncus sapien a libero luctus, sed condimentum arcu feugiat. Fusce efficitur turpis et risus placerat, vel feugiat sapien interdum.


    Args:
        x (str): Duis at ultricies mauris. Phasellus ac tortor ut dolor accumsan fermentum. Curabitur vitae nunc vitae quam iaculis aliquet.
        y (int):  Proin fringilla dui nec tincidunt pretium. Ut semper felis a justo ullamcorper, eget tincidunt lectus ultricies.
        f (float): Maecenas vestibulum dolor ut metus scelerisque, a ullamcorper velit suscipit. Suspendisse potenti. Phasellus vel leo purus.
        int_with_optional (int | None): Consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        p (Path | None): Sed ac malesuada arcu. Vivamus et ultricies urna, ac feugiat est. Curabitur ultrices lorem eu erat venenatis, quis cursus tortor mattis.
        enum (Dummy_Enum):  Nam efficitur sollicitudin metus, sit amet vestibulum lorem rutrum in.
        enum_tuple (tuple[Dummy_Enum, Dummy_Enum]): Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Vestibulum luctus urna vel mi fringilla, sit amet posuere lorem commodo.
        list_str (list[str]): Nunc eget libero in purus faucibus consequat. Mauris accumsan eros sit amet odio consectetur, ut varius mi vehicula. Nam commodo elit sit amet nisl cursus fermentum.
        list_int (list[int]): Sed sollicitudin, nulla nec efficitur consectetur, felis mi cursus nulla, eget faucibus turpis lacus non nisi. Proin et eros non ex rutrum congue. Nulla facilisi.
        tuple_any_len (tuple[str, ...]): Suspendisse potenti. Nullam eleifend magna eget ante congue, ac sodales quam pellentesque. Ut euismod interdum urna, sit amet iaculis quam convallis vel.
        tuple_with_fixed_lenght (tuple[str, str]): Donec nec faucibus est. Nullam id nisi eget sem laoreet interdum. Proin efficitur tortor sed diam tincidunt, et convallis mauris rhoncus. Ut non sapien at eros volutpat vehicula. Morbi pharetra ipsum nec lorem molestie, in consectetur dui convallis.
        set_s (set[str]):  Nulla ac risus ut lorem cursus bibendum. Duis et ante auctor, lacinia elit id, vestibulum sapien. Maecenas ac risus sit amet mauris vestibulum pharetra nec et sem. Nam nec nibh non nunc sollicitudin efficitur.
        set_i (set[int]):Fusce tincidunt tortor id quam commodo eleifend. Curabitur ullamcorper metus in efficitur tempus. Vestibulum et aliquet leo. Nam non turpis sapien.
        b (bool): Morbi dapibus orci nec semper iaculis.
    """

    x: str = "Your API key now on GitHub"
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
```

will produce this help string:

```
python _Readme.py -h
usage: _Readme.py [-h] [-config CONFIG] [--b] [--enum {ONE,SECOND,THIRD}] [--enum_tuple {ONE,SECOND,THIRD} [{ONE,SECOND,THIRD} ...]] [--f F] [--int_with_optional INT_WITH_OPTIONAL] [--list_int LIST_INT [LIST_INT ...]]
                  [--list_str LIST_STR [LIST_STR ...]] [--p P] [--set_i SET_I [SET_I ...]] [--set_s SET_S [SET_S ...]] [--tuple_any_len TUPLE_ANY_LEN [TUPLE_ANY_LEN ...]]
                  [--tuple_with_fixed_lenght TUPLE_WITH_FIXED_LENGHT [TUPLE_WITH_FIXED_LENGHT ...]] [--x X] [--y Y]

options:
  -h, --help            show this help message and exit
  -config CONFIG, --config CONFIG
                        config file path
  --b                   Morbi dapibus orci nec semper iaculis.
  --enum {ONE,SECOND,THIRD}
                        Nam efficitur sollicitudin metus, sit amet vestibulum lorem rutrum in.
  --enum_tuple {ONE,SECOND,THIRD} [{ONE,SECOND,THIRD} ...]
                        Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Vestibulum luctus urna vel mi fringilla, sit amet posuere lorem commodo.
  --f F                 Maecenas vestibulum dolor ut metus scelerisque, a ullamcorper velit suscipit. Suspendisse potenti. Phasellus vel leo purus.
  --int_with_optional INT_WITH_OPTIONAL
                        Consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
  --list_int LIST_INT [LIST_INT ...]
                        Sed sollicitudin, nulla nec efficitur consectetur, felis mi cursus nulla, eget faucibus turpis lacus non nisi. Proin et eros non ex rutrum congue. Nulla facilisi.
  --list_str LIST_STR [LIST_STR ...]
                        Nunc eget libero in purus faucibus consequat. Mauris accumsan eros sit amet odio consectetur, ut varius mi vehicula. Nam commodo elit sit amet nisl cursus fermentum.
  --p P                 Sed ac malesuada arcu. Vivamus et ultricies urna, ac feugiat est. Curabitur ultrices lorem eu erat venenatis, quis cursus tortor mattis.
  --set_i SET_I [SET_I ...]
                        Fusce tincidunt tortor id quam commodo eleifend. Curabitur ullamcorper metus in efficitur tempus. Vestibulum et aliquet leo. Nam non turpis sapien.
  --set_s SET_S [SET_S ...]
                        Nulla ac risus ut lorem cursus bibendum. Duis et ante auctor, lacinia elit id, vestibulum sapien. Maecenas ac risus sit amet mauris vestibulum pharetra nec et sem. Nam nec nibh non nunc sollicitudin
                        efficitur.
  --tuple_any_len TUPLE_ANY_LEN [TUPLE_ANY_LEN ...]
                        Suspendisse potenti. Nullam eleifend magna eget ante congue, ac sodales quam pellentesque. Ut euismod interdum urna, sit amet iaculis quam convallis vel.
  --tuple_with_fixed_lenght TUPLE_WITH_FIXED_LENGHT [TUPLE_WITH_FIXED_LENGHT ...]
                        Donec nec faucibus est. Nullam id nisi eget sem laoreet interdum. Proin efficitur tortor sed diam tincidunt, et convallis mauris rhoncus. Ut non sapien at eros volutpat vehicula. Morbi pharetra ipsum nec     
                        lorem molestie, in consectetur dui convallis.
  --x X                 Duis at ultricies mauris. Phasellus ac tortor ut dolor accumsan fermentum. Curabitur vitae nunc vitae quam iaculis aliquet.
  --y Y                 Proin fringilla dui nec tincidunt pretium. Ut semper felis a justo ullamcorper, eget tincidunt lectus ultricies.

Args that start with '--' can also be set in a config file (specified via -config). Config file syntax allows: key=value, flag=true, stuff=[a,b,c] (for details, see syntax at https://goo.gl/R74nmi). In general, command-line values  
override config file values which override defaults.
```