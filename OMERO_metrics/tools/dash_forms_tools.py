import dash_mantine_components as dmc
from dataclasses import fields
from dash_iconify import DashIconify
import re

Field_TYPE_MAPPING = {
    "float": "NumberInput",
    "int": "NumberInput",
    "str": "TextInput",
    "bool": "Checkbox",
}


def extract_form_data(form_content):
    return {i["props"]["id"]: i["props"]["value"] for i in form_content}


def disable_all_fields_dash_form(form):
    for i, t in enumerate(form):
        form[i]["props"]["disabled"] = True
    return form


def clean_field_name(field: str):
    return field.replace("_", " ").title()


def get_field_types(field, supported_types=["str", "int", "float", "bool"]):
    data_type = {
        "field_name": clean_field_name(field.name),
        "type": None,
        "optional": False,
        "default": field.default,
    }
    if field.type.__name__ == "Optional":
        data_type["type"] = field.type.__args__[0].__name__
        data_type["optional"] = True
    elif field.type.__name__ == "Union":
        data_type["type"] = field.type.__args__[0].__name__
    elif field.type.__name__ in supported_types:
        data_type["type"] = field.type.__name__
    else:
        print(f'Field type "{field.type}" not supported')
        data_type["type"] = "unsupported"
    return data_type


def get_dmc_field_input(
    field, type_mapping=Field_TYPE_MAPPING, disabled=False
):
    field_info = get_field_types(field)
    input_field_name = getattr(dmc, type_mapping[field_info["type"]])
    input_field = input_field_name()
    input_field.id = field_info["field_name"].replace(" ", "_").lower()
    input_field.label = field_info["field_name"]
    input_field.placeholder = "Enter " + field_info["field_name"]
    input_field.value = field_info["default"]
    input_field.w = "300"
    input_field.disabled = disabled
    input_field.required = not field_info["optional"]
    input_field.leftSection = DashIconify(icon="radix-icons:ruler-horizontal")
    # if not field_info['optional']:
    #     input_field.error = "This field is required"
    return input_field


def validate_form(state):
    return all(
        i["props"]["id"] == "submit_id"
        or not (
            i["props"]["required"]
            and i["props"]["value"] is None
            or i["props"]["value"] == ""
        )
        for i in state
    )


def add_space_between_capitals(s: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", s)


class dashForm:
    def __init__(self, mm_object, disabled=False, form_id="form_content"):
        self.mm_object = mm_object
        self.disabled = disabled
        self.form_id = form_id
        self.form = self.get_form()

    def get_form(self):
        form_content = dmc.Stack(
            id=self.form_id,
            children=[],
            align="center",
            style={
                "width": "auto",
                "height": "auto",
                "border-radius": "0.5rem",
                "padding": "10px",
                "border": "1px solid #189A35",
            },
        )
        for field in fields(self.mm_object):
            form_content.children.append(
                get_dmc_field_input(field, disabled=self.disabled)
            )
        # form_content.children.append(
        #     dmc.Button(
        #         id="submit_id", children=["Submit"], color="green", n_clicks=0
        #     )
        # )
        return form_content
