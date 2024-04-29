import argparse
from enum import Enum


def translation_enum_to_str(enum: type[Enum]) -> list[str]:
    return [v.name for v in enum]


def class_to_str(s):
    if issubclass(s, Enum):
        return str([f for f in dir(s) if not f.startswith("__")])
    return str(s).replace("<class '", "").replace("'>", "")


def len_checker(s, num_elements, org_annotation, can_be_none, name):
    print(s, num_elements)
    if can_be_none and s is None:
        return s
    if str(s) == "<factory>":
        return s
    if len(s) == num_elements:
        return s
    raise argparse.ArgumentTypeError(
        f"Tuple named '{name}' must must have length of {num_elements} by the definition: {org_annotation};\n A tuple has a fixed lenght, except when the definition ends with ...; Like: tuple[int,...]"
    )
