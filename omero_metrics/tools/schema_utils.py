from functools import lru_cache
from typing import Union, get_args, get_type_hints

from microscopemetrics.analyses.mappings import MAPPINGS
from microscopemetrics_schema.datamodel import microscopemetrics_schema as mm_schema
from microscopemetrics_schema.datamodel.microscopemetrics_schema import Image


@lru_cache(maxsize=None)
def get_image_fields(dataset_class) -> dict[str, list[str]]:
    """Introspect a dataset class to find Image-typed fields per location.

    Returns a dict mapping location names ('input_data', 'output') to lists
    of field names that are typed as Image or list[Image].
    """
    result = {}
    hints = get_type_hints(dataset_class)
    for location in ("input_data", "output"):
        location_hint = hints.get(location)
        if location_hint is None:
            result[location] = []
            continue
        # Resolve Union/Optional to find the actual sub-class (not dict/NoneType)
        sub_cls = None
        for arg in get_args(location_hint):
            if arg is not dict and arg is not type(None):
                sub_cls = arg
                break
        if sub_cls is None:
            result[location] = []
            continue
        # Find fields whose type includes Image
        image_fields = []
        for field_name, field_type in get_type_hints(sub_cls).items():
            all_args = get_args(field_type) or (field_type,)
            if any(a is Image or Image in get_args(a) for a in all_args):
                image_fields.append(field_name)
        result[location] = image_fields
    return result


@lru_cache(maxsize=None)
def get_dataset_class(input_parameters_class):
    """Find the MetricsDataset subclass whose input_parameters field is typed as the given class."""
    for subclass in mm_schema.MetricsDataset.__subclasses__():
        for arg in get_args(
            get_type_hints(subclass).get("input_parameters", None) or ()
        ):
            if arg is input_parameters_class:
                return subclass
    raise ValueError(
        f"No Dataset class found for input parameters class {input_parameters_class}"
    )


@lru_cache(maxsize=None)
def get_input_data_class(dataset_class):
    """Resolve the InputData class from a dataset class's input_data type hint."""
    for arg in get_args(get_type_hints(dataset_class).get("input_data")):
        if arg is not dict and arg is not type(None):
            return arg
    raise ValueError(f"No InputData class found for {dataset_class}")


def get_analysis_function(dataset_class):
    """Find the analysis function for a given dataset class from microscopemetrics MAPPINGS."""
    try:
        return MAPPINGS[dataset_class].analysis_function
    except KeyError as e:
        raise ValueError(f"No analysis function found for {dataset_class}") from e


def remove_unsupported_types(
    data_obj: Union[
        mm_schema.MetricsInputData,
        mm_schema.MetricsInputParameters,
        mm_schema.MetricsOutput,
    ],
):
    def _remove(_attr):
        if isinstance(_attr, mm_schema.Image):
            _attr.array_data = None
        elif isinstance(_attr, mm_schema.Table):
            _attr.table_data = None
        elif isinstance(_attr, mm_schema.Roi):
            if _attr.masks:
                for m in _attr.masks:
                    _remove(m.mask)

    with contextlib.suppress(TypeError):
        for field in fields(data_obj):
            try:
                _attr = getattr(data_obj, field.name)
                if isinstance(_attr, list):
                    [_remove(i) for i in _attr]
                else:
                    _remove(_attr)
            except AttributeError:
                continue
