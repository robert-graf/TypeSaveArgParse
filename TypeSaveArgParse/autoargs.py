import argparse
import dataclasses
import sys
import types
from argparse import ArgumentParser
from dataclasses import Field, asdict, dataclass, field
from enum import Enum
from functools import partial
from inspect import signature
from pathlib import Path
from typing import get_args, get_origin

from TypeSaveArgParse.utils import class_to_str, len_checker, translation_enum_to_str

config_help = "config file path"


@dataclass()
class Class_to_ArgParse:
    @classmethod
    def get_opt(cls, parser: None | ArgumentParser = None, default_config=None):
        _checks = {}
        if parser is None:
            p: ArgumentParser = ArgumentParser()
            p.add_argument("-config", "--config", default=default_config, type=str, help=config_help)
        else:
            p = parser

        # fetch the constructor's signature
        parameters = signature(cls).parameters
        cls_fields = sorted(set(parameters))

        # split the kwargs into native ones and new ones
        for name in cls_fields:
            can_be_none = False
            key = "--" + name
            default = parameters[name].default
            annotation = parameters[name].annotation

            # Handling :A |B |...| None (None means Optional argument)
            annotations = []
            if get_origin(annotation) == types.UnionType:
                for i in get_args(annotation):
                    if i == types.NoneType:
                        can_be_none = True
                    else:
                        annotations.append(i)
                        annotation = i
            if len(annotations) > 1:
                raise NotImplementedError("UnionType", annotations)  # TODO
            del annotations
            # Handling :bool = [True | False]
            if annotation == bool:
                if default:
                    p.add_argument(key, action="store_false", default=True)
                else:
                    p.add_argument(key, action="store_true", default=False)
                continue
            # Handling :subclass of Enum
            elif isinstance(default, Enum) or issubclass(annotation, Enum):
                p.add_argument(key, default=default, choices=translation_enum_to_str(annotation))
            # Handling :list,tuple,set
            elif get_origin(annotation) == list or get_origin(annotation) == tuple or get_origin(annotation) == set:
                # Unpack Sequence[...] -> ...
                org_annotation = annotation
                annotations = []
                had_ellipsis = False
                for i in get_args(annotation):
                    if i == types.NoneType:
                        default = None
                    elif i == Ellipsis:
                        had_ellipsis = True
                    else:
                        annotations.append(i)
                        annotation = i
                num_ann = len(annotations)
                annotations_s = set(annotations)
                assert not (get_origin(annotation) == tuple and not had_ellipsis)
                if get_origin(org_annotation) == tuple and not had_ellipsis:
                    # Tuple with fixed size
                    _checks[name] = partial(
                        len_checker, num_elements=num_ann, org_annotation=org_annotation, can_be_none=can_be_none, name=name
                    )
                if len(annotations_s) != 1:
                    raise NotImplementedError("Non uniform sequence", annotations)
                elif issubclass(annotation, Enum):
                    choices = [f for f in dir(annotation) if not f.startswith("__")]
                    p.add_argument(key, nargs="+", default=default, type=str, help="List of keys", choices=choices)
                else:
                    p.add_argument(key, nargs="+", default=default, type=annotation, help="List of " + class_to_str(annotation))
            else:
                p.add_argument(key, default=default, type=annotation)
        # if return_partial_parser:
        #    return p
        return cls.from_kwargs(**p.parse_args().__dict__, _checks=_checks)

    @classmethod
    def from_kwargs(cls, _checks=None, **kwargs):
        # fetch the constructor's signature
        if _checks is None:
            _checks = {}
        parameters = signature(cls).parameters
        cls_fields = set(parameters)
        # split the kwargs into native ones and new ones
        native_args, new_args = {}, {}
        for name, val2 in kwargs.items():
            val = val2
            if name in cls_fields:
                # Cast Str to Enum
                if isinstance(parameters[name].default, Enum):
                    try:
                        val = parameters[name].annotation[val]
                    except KeyError:
                        print(f"Enum {type(parameters[name].default)} has no {val}")
                        sys.exit(1)

                # Cast list to Set/Tuple:
                def cast_from_list(type_, val, name):
                    if get_origin(parameters[name].annotation) == type_:
                        return type_(val) if isinstance(val, list) else val
                    return val

                val = cast_from_list(set, val, name)
                val = cast_from_list(tuple, val, name)
                native_args[name] = val
            else:
                new_args[name] = val
            _checks.get(name, id)(val)
        ret = cls(**native_args)
        # ... and add the new ones by hand
        for new_name, new_val in new_args.items():
            setattr(ret, new_name, new_val)
        return ret

    def __getstate__(self):
        """Replace fields, so that they can be pickeled"""
        state = self.__dict__.copy()
        for key, value in state.items():
            if isinstance(value, Field):
                if isinstance(value.default, dataclasses._MISSING_TYPE):
                    state[key] = value.default_factory()  # type: ignore

                else:
                    state[key] = value.default
                self.__dict__[key] = state[key]
        return state
