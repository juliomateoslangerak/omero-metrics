import dash_mantine_components as dmc
from dataclasses import fields
from dash_iconify import DashIconify
import re
from typing import get_origin, get_args, Union


Field_TYPE_MAPPING = {
    "float": [dmc.NumberInput, "carbon:character-decimal"],
    "int": [dmc.NumberInput, "carbon:character-whole-number"],
    "str": [dmc.TextInput, "carbon:string-text"],
}


def extract_form_data(form_content, class_name):
    replace_str = f"^{class_name}_"
    return {
        i["props"]["id"].replace(replace_str, "", regex=True): i["props"][
            "value"
        ]
        for i in form_content
    }


def disable_all_fields_dash_form(form):
    for i, t in enumerate(form):
        form[i]["props"]["disabled"] = True
    return form


def clean_field_name(field: str):
    return field.replace("_", " ").title()


def get_field_types(field, supported_types=(str, int, float, bool)):
    data_type = {
        "field_name": field.name,
        "type": None,
        "optional": False,
        "default": field.default,
    }
    if get_origin(field.type) is Union:
        args = get_args(field.type)
        if args[1] is type(None):
            data_type["optional"] = True
            data_type["type"] = args[0].__name__
        elif args[0] in supported_types:
            data_type["type"] = args[0].__name__
        else:
            data_type["type"] = "unsupported"
    elif field.type in supported_types:
        data_type["type"] = field.type.__name__
    else:
        data_type["type"] = "unsupported"
    return data_type


def get_dmc_field_input(
    field, mm_object, type_mapping=Field_TYPE_MAPPING, disabled=False
):
    field_info = get_field_types(field)
    input_field_name = type_mapping[field_info["type"]][0]
    input_field = input_field_name()
    input_field.id = f"{mm_object.class_name}_{field_info['field_name']}"
    input_field.label = clean_field_name(field_info["field_name"])
    input_field.placeholder = (
        f"Enter {clean_field_name(field_info['field_name'])}"
    )
    input_field.value = (
        field_info["default"]
        if getattr(mm_object, field.name) is None
        else getattr(mm_object, field.name)
    )
    input_field.w = "auto"
    input_field.disabled = disabled
    input_field.required = not field_info["optional"]
    input_field.leftSection = DashIconify(
        icon=type_mapping[field_info["type"]][1]
    )
    input_field.maxWidth = "450px"

    return input_field


def validate_form(state):
    return all(
        i["props"]["id"] == "submit_id"
        or not (
            i["props"]["required"]
            and (i["props"]["value"] is None or i["props"]["value"] == "")
        )
        for i in state
    )


def add_space_between_capitals(s: str) -> str:
    label = re.sub(r"(?<!^)(?=[A-Z])", " ", s)
    label = label.replace("P S F", "PSF")
    return label


def get_form(mm_object, disabled=False, form_id="form_content"):
    form_content = dmc.Fieldset(
        id=form_id,
        children=[],
        legend=add_space_between_capitals(mm_object.class_name),
        variant="filled",
        radius="md",
    )
    for field in fields(mm_object):
        form_content.children.append(
            get_dmc_field_input(field, mm_object, disabled=disabled)
        )
    return form_content
