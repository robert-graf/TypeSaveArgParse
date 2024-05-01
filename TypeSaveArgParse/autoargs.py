import dataclasses
import sys
import types
from dataclasses import Field, asdict, dataclass, field
from enum import Enum
from functools import partial
from inspect import signature
from pathlib import Path
from typing import get_args, get_origin

from configargparse import ArgumentParser

from TypeSaveArgParse.utils import cast_all, cast_if_enum, cast_if_list_to, class_to_str, len_checker, translation_enum_to_str

config_help = "config file path"


@dataclass()
class Class_to_ArgParse:
    @classmethod
    def get_opt(cls, parser: None | ArgumentParser = None, default_config=None):
        _checks = {}
        _enum = {}
        if parser is None:
            p: ArgumentParser = ArgumentParser()
            p.add_argument("-config", "--config", is_config_file_arg=True, default=default_config, type=str, help=config_help)
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
                _enum[name] = annotation
                p.add_argument(key, default=default, choices=translation_enum_to_str(annotation))
            # Handling :list,tuple,set
            elif get_origin(annotation) in (list, tuple, set):
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
                    _enum[name] = annotation
                else:
                    p.add_argument(key, nargs="+", default=default, type=annotation, help="List of " + class_to_str(annotation))
            else:
                p.add_argument(key, default=default, type=annotation)
        # if return_partial_parser:
        #    return p

        out = cls.from_kwargs(**p.parse_args().__dict__, _checks=_checks, _enum=_enum)
        return out

    @classmethod
    def from_kwargs(cls, _checks=None, _enum=None, **kwargs):
        # fetch the constructor's signature
        if _enum is None:
            _enum = {}
        if _checks is None:
            _checks = {}
        parameters = signature(cls).parameters
        cls_fields = set(parameters)
        # split the kwargs into native ones and new ones
        native_args, new_args = {}, {}
        for name, val2 in kwargs.items():
            val = val2
            if name in cls_fields:
                # recursive call on list HERE
                val = cast_all(val, parameters[name], _enum.get(name, None))
                native_args[name] = val
            else:
                # unknown parameters
                new_args[name] = val
            _checks.get(name, id)(val)
        ret = cls(**native_args)
        # ... and add the new ones by hand
        for new_name, new_val in new_args.items():
            setattr(ret, new_name, new_val)
        return ret

    def __getstate__(self):
        """Replace fields, so that they can be pickled"""
        state = self.__dict__.copy()
        for key, value in state.items():
            if isinstance(value, Field):
                if isinstance(value.default, dataclasses._MISSING_TYPE):
                    state[key] = value.default_factory()  # type: ignore

                else:
                    state[key] = value.default
                self.__dict__[key] = state[key]
        return state

    def save_config(self, outfile: str | Path, default_flow_style: None | bool = None):
        import ruamel.yaml
        import ruamel.yaml as ryaml
        # import yaml

        with open(outfile, "w") as out_file_stream:
            y = ryaml.YAML()  # typ="safe", pure=True
            y.default_flow_style = default_flow_style
            data = ruamel.yaml.CommentedMap()
            start_comment = ""
            parameters = signature(self.__class__).parameters
            cls_fields = sorted(set(parameters))
            pref = None
            for k, v in asdict(self).items():
                if k.startswith("_"):
                    continue
                if v is None:
                    att = ""
                    try:
                        att = str(getattr(self, k))
                    except Exception:
                        pass
                    s = f"{k}: {att} # {parameters[k].annotation}\n"
                    if pref is None:
                        start_comment += s
                    else:
                        data.yaml_set_comment_before_after_key(pref, before=s, indent=0)
                    continue
                if isinstance(v, (list, set, tuple)) and len(v) == 0:
                    att = ""
                    try:
                        att = str(getattr(self, k))
                    except Exception:
                        pass

                    s = f"{k}: {att} # {parameters[k].annotation}\n"
                    if pref is None:
                        start_comment += s
                    else:
                        data.yaml_set_comment_before_after_key(pref, before=s, indent=0)

                    continue
                if isinstance(v, (list, set, tuple)):

                    def enum_to_str(i):
                        if isinstance(i, Enum):
                            return i.name
                        return i

                    v = [enum_to_str(i) for i in v]  # noqa: PLW2901
                if isinstance(v, Enum):
                    v = v.name  # noqa: PLW2901
                elif isinstance(v, Path):
                    v = str(v)  # noqa: PLW2901
                elif isinstance(v, set):
                    v = list(v)  # noqa: PLW2901
                pref = k
                data[k] = v
            # fetch the constructor's signature
            if len(start_comment) != 0:
                data.yaml_set_start_comment(start_comment)

            # split the kwargs into native ones and new ones
            for name in cls_fields:
                can_be_none = False
                default = parameters[name].default
                default = "" if str(default) == "<factory>" else f"- default [{default}]"
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
                    continue
                del annotations
                # Handling :bool = [True | False]
                if annotation == bool:
                    data.yaml_add_eol_comment(f"[True|False] {default}", name)

                # Handling :subclass of Enum
                elif isinstance(default, Enum) or issubclass(annotation, Enum):
                    s = f"{annotation} Choices:{translation_enum_to_str(annotation)} {default}"
                    data.yaml_add_eol_comment(s, name)
                ## Handling :list,tuple,set
                elif get_origin(annotation) in (list, tuple, set):
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
                    if get_origin(org_annotation) == tuple and not had_ellipsis:
                        s = f"Note: Tuple with a fixed size of {num_ann}"
                        data.yaml_set_comment_before_after_key(name, before=s)

                    if issubclass(annotation, Enum):
                        s = f"{annotation} Choices:{translation_enum_to_str(annotation)} {default}"
                        data.yaml_add_eol_comment(s, name)
            y.dump(data, out_file_stream)
        # Could not find to use "" for strings instead of ''.
        # So we have this solution
        # Thanks I hate it. (pyYaml need "" or it would cas 'x' to "'x'" instead of "x")
        with open(outfile) as out_file_stream:
            data = out_file_stream.read()
        with open(outfile, "w") as out_file_stream:
            out_file_stream.write(data.replace("'", '"'))


# data = ruamel.yaml.round_trip_load(outfile)

# data["test1"].yaml_set_start_comment("before test2", indent=2)
# data["test1"]["test2"].yaml_set_start_comment("after test2", indent=4)
# ruamel.yaml.round_trip_dump(data, sys.stdout)


# ryaml.safe_dump(asdict(self), outfile, default_flow_style=default_flow_style, sort_keys=False)
