import dataclasses
import re
from dataclasses import fields
from typing import Union, get_args, get_origin

import dash_mantine_components as dmc
from dash_iconify import DashIconify

# TODO: Modify the schema to make this a mm_schema class
from linkml_runtime.utils.metamodelcore import XSDDateTime

# These mappings must be ordered by priority
FIELD_TYPE_MAPPING = {
    XSDDateTime: [dmc.DateTimePicker, "carbon:calendar"],
    float: [dmc.NumberInput, "carbon:character-decimal"],
    int: [dmc.NumberInput, "carbon:character-whole-number"],
    bool: [dmc.Switch, "carbon:switch-disabled"],
    str: [dmc.TextInput, "carbon:string-text"],
}


def extract_form_data(form_content):
    result = {}
    for item in form_content:
        if item.get("type") == "Fieldset":
            field_name = item["props"]["id"].split(":")[-1]
            result[field_name] = extract_form_data(item["props"]["children"])
        else:
            field_name = item["props"]["id"].split(":")[1]
            result[field_name] = item["props"]["value"]
    return result


def disable_all_fields_dash_form(form):
    for i, t in enumerate(form):
        form[i]["props"]["disabled"] = True
    return form


def clean_field_name(field: str):
    return field.replace("_", " ").title()


def get_field_types(field):
    data_type = {
        "field_name": field.name,
        "type": None,
        "optional": False,
        "default": field.default,
        "is_dataclass": False,
    }
    if get_origin(field.type) is Union:
        args = get_args(field.type)
        # Check if it's Optional (Union with None)
        if type(None) in args:
            data_type["optional"] = True
            args = [arg for arg in args if arg is not type(None)]

        # Check for a nested dataclass before scalar type matching
        dc_args = [a for a in args if dataclasses.is_dataclass(a)]
        if dc_args:
            data_type["type"] = dc_args[0]
            data_type["is_dataclass"] = True
            return data_type

        # Select type by priority based on FIELD_TYPE_MAPPING order
        for priority_type in FIELD_TYPE_MAPPING.keys():
            if priority_type in args:
                data_type["type"] = priority_type
                break

    elif dataclasses.is_dataclass(field.type):
        data_type["type"] = field.type
        data_type["is_dataclass"] = True

    elif field.type in FIELD_TYPE_MAPPING.keys():
        data_type["type"] = field.type

    else:
        raise TypeError(
            f"A corresponding datatype could not be found for form field {field}"
        )

    return data_type


def get_dmc_field_input(field, mm_object, disabled=False):
    field_info = get_field_types(field)
    input_field_name = FIELD_TYPE_MAPPING[field_info["type"]][0]
    input_field = input_field_name()
    input_field.id = f"{mm_object.class_name}:{field_info['field_name']}"
    input_field.label = clean_field_name(field_info["field_name"])
    input_field.placeholder = f"Enter {clean_field_name(field_info['field_name'])}"
    input_field.value = (
        field_info["default"]
        if getattr(mm_object, field.name) is None
        else getattr(mm_object, field.name)
    )
    input_field.w = "auto"
    input_field.disabled = disabled
    input_field.required = not field_info["optional"]
    input_field.leftSection = DashIconify(
        icon=FIELD_TYPE_MAPPING[field_info["type"]][1]
    )
    input_field.maxWidth = "450px"

    return input_field


def validate_form(state):
    for item in state:
        if item.get("type") == "Fieldset":
            if not validate_form(item["props"]["children"]):
                return False
        elif item["props"].get("required") and not item["props"].get("value"):
            return False
    return True


def add_space_between_capitals(s: str) -> str:
    label = re.sub(r"(?<!^)(?=[A-Z])", " ", s)
    label = label.replace("P S F", "PSF")
    return label


def get_form(mm_dataclass, disabled=False, form_id="form_content"):
    form_content = dmc.Fieldset(
        id=form_id,
        children=[],
        # TODO: we have to rather rely on the title of the class
        legend=dmc.Text(
            add_space_between_capitals(mm_dataclass.class_name),
            fw=700,
            fz="md",  # or fz="lg" for larger
        ),
        variant="filled",
        radius="md",
    )
    for field in fields(mm_dataclass):
        field_info = get_field_types(field)
        if field_info["is_dataclass"]:
            form_content.children.append(
                get_form(
                    mm_dataclass=field_info["type"],
                    disabled=disabled,
                    form_id=f"{form_id}:{field.name}",
                )
            )
        elif field_info["type"] is not None:
            form_content.children.append(
                get_dmc_field_input(field, mm_dataclass, disabled=disabled)
            )
    return form_content
