import dataclasses
import json
import re
from abc import ABC, abstractmethod
from dataclasses import fields
from typing import Any, Union, get_args, get_origin

import dash
import dash_mantine_components as dmc
from dash_iconify import DashIconify

# TODO: Modify the schema to make this a mm_schema class
from linkml_runtime.utils.metamodelcore import XSDDateTime


class GrowingListBase(ABC):
    subtype: str  # overridden in each concrete subclass

    def __init__(
        self,
        id: str,
        label: str = "",
        value=None,
        disabled: bool = False,
        input_kwargs=None,
    ):
        self.id = id
        self.label = label
        self.initial = value or []
        self.disabled = disabled
        self.input_kwargs = input_kwargs or {}

    @property
    def wrapper_id(self):
        return {
            "type": "growing-list-fieldset",
            "subtype": self.subtype,
            "owner": self.id,
        }

    @property
    def stack_id(self):
        return {
            "type": "growing-list-stack",
            "subtype": self.subtype,
            "owner": self.id,
        }

    @property
    def add_btn_id(self):
        return {
            "type": "growing-list-add",
            "subtype": self.subtype,
            "owner": self.id,
        }

    @property
    def remove_btn_id(self):
        return {
            "type": "growing-list-remove",
            "subtype": self.subtype,
            "owner": self.id,
        }

    def input_id(self, index):
        return {
            "type": "growing-list-input",
            "subtype": self.subtype,
            "owner": self.id,
            "index": index,
        }

    def _button_group(self):
        return dmc.Group(
            [
                dmc.ActionIcon(
                    DashIconify(icon="carbon:add"),
                    id=self.add_btn_id,
                    variant="subtle",
                    color="green",
                    size="sm",
                ),
                dmc.ActionIcon(
                    DashIconify(icon="carbon:subtract"),
                    id=self.remove_btn_id,
                    variant="subtle",
                    color="red",
                    size="sm",
                ),
            ],
            mt="xs",
            gap="xs",
        )

    def layout(self):
        initial = self.initial if self.initial else [None]
        return dmc.InputWrapper(
            id=self.wrapper_id,
            label=self.label,
            required=not self.disabled,
            children=dmc.Stack(
                id=self.stack_id,
                children=self._build_children(initial),
                gap="xs",
            ),
        )

    def _build_children(self, values):
        children = [self.make_input(i, v) for i, v in enumerate(values)]
        if not self.disabled:
            children.append(self._button_group())
        return children

    @abstractmethod
    def make_input(self, index, value):
        """Return the appropriate Dash component."""

    def clean(self, values):
        return [value for value in values if value not in ("", None)]


class GrowingFloatList(GrowingListBase):
    subtype = "float"

    def make_input(self, index, value):
        return dmc.NumberInput(
            id=self.input_id(index),
            value=value,
            disabled=self.disabled,
            allowDecimal=True,
            **self.input_kwargs,
        )


class GrowingIntList(GrowingListBase):
    subtype = "int"

    def make_input(self, index, value):
        return dmc.NumberInput(
            id=self.input_id(index),
            value=value,
            disabled=self.disabled,
            allowDecimal=False,
            **self.input_kwargs,
        )


class GrowingStringList(GrowingListBase):
    subtype = "str"

    def make_input(self, index, value):
        return dmc.TextInput(
            id=self.input_id(index),
            value=value,
            disabled=self.disabled,
            **self.input_kwargs,
        )


def _make_growing_list_callback(app, cls):
    @app.expanded_callback(
        dash.Output(
            {
                "type": "growing-list-stack",
                "subtype": cls.subtype,
                "owner": dash.MATCH,
            },
            "children",
        ),
        [
            dash.Input(
                {
                    "type": "growing-list-add",
                    "subtype": cls.subtype,
                    "owner": dash.MATCH,
                },
                "n_clicks",
            ),
            dash.Input(
                {
                    "type": "growing-list-remove",
                    "subtype": cls.subtype,
                    "owner": dash.MATCH,
                },
                "n_clicks",
            ),
            dash.State(
                {
                    "type": "growing-list-input",
                    "subtype": cls.subtype,
                    "owner": dash.MATCH,
                    "index": dash.ALL,
                },
                "value",
            ),
        ],
        prevent_initial_call=True,
    )
    def update(_add, _remove, current_values, **kwargs):
        ctx = kwargs["callback_context"]
        prop_id = ctx.triggered[0]["prop_id"]
        # prop_id looks like: '{"owner":"...","subtype":"float","type":"growing-list-add"}.n_clicks'
        triggered_id = json.loads(prop_id.rsplit(".", 1)[0])
        triggered_type = triggered_id["type"]
        owner = triggered_id["owner"]

        instance = cls(id=owner)
        values = list(current_values) if current_values else [None]

        if triggered_type == "growing-list-add":
            values = values + [None]
        elif triggered_type == "growing-list-remove" and len(values) > 1:
            values = values[:-1]

        return instance._build_children(values)


def register_growing_list_callbacks(app):
    """Register GrowingList +/- callbacks on a DjangoDash app instance.

    Call this once per app that uses render_fieldset with list fields.
    """
    for cls in (GrowingFloatList, GrowingIntList, GrowingStringList):
        _make_growing_list_callback(app, cls)


def _dmc_builder(cls, *, placeholder: bool = True):
    """Return a builder for a standard DMC input component."""

    def build(resolved: "ResolvedField", icon: str, disabled: bool):
        field_name = resolved.name.split(":")[-1]
        kwargs = dict(
            id=f"field-{resolved.name}",
            label=clean_field_name(field_name),
            value=resolved.render_value,
            w="auto",
            disabled=disabled,
            required=not resolved.optional,
            leftSection=DashIconify(icon=icon),
        )
        if placeholder:
            kwargs["placeholder"] = f"Enter {field_name.replace('_', ' ')}"
        return cls(**kwargs)

    return build


def _growing_list_builder(cls):
    """Return a builder for a GrowingListBase subclass."""

    def build(resolved: "ResolvedField", icon: str, disabled: bool):
        field_name = resolved.name.split(":")[-1]
        instance = cls(
            id=f"field-{resolved.name}",
            label=clean_field_name(field_name),
            value=resolved.render_value or [],
            disabled=disabled,
        )
        return instance.layout()

    return build


# These mappings must be ordered by priority.
# Each value is (builder_callable, icon_string).
FIELD_TYPE_MAPPING = {
    XSDDateTime: (
        _dmc_builder(dmc.DateTimePicker, placeholder=False),
        "carbon:calendar",
    ),
    list[float]: (
        _growing_list_builder(GrowingFloatList),
        "carbon:character-decimal",
    ),
    list[int]: (
        _growing_list_builder(GrowingIntList),
        "carbon:character-whole-number",
    ),
    list[str]: (
        _growing_list_builder(GrowingStringList),
        "carbon:character-whole-number",
    ),
    float: (_dmc_builder(dmc.NumberInput), "carbon:character-decimal"),
    int: (_dmc_builder(dmc.NumberInput), "carbon:character-whole-number"),
    bool: (_dmc_builder(dmc.Switch, placeholder=False), "carbon:switch-disabled"),
    str: (_dmc_builder(dmc.TextInput), "carbon:string-text"),
}


@dataclasses.dataclass
class ResolvedField:
    name: str
    optional: bool
    value: Any  # instance value when resolved from an instance, else class default
    hint: str
    primitive_type: type | None  # key into FIELD_TYPE_MAPPING; None when nested
    nested_type: type | None  # dataclass class when nested; None when primitive

    @property
    def render_value(self):
        """The value to render."""
        return self.value


def resolve_field_type(
    field, parent_name: str = "", instance=None
) -> ResolvedField | None:
    """Resolve a dataclass field's type to a ResolvedField descriptor.

    When ``instance`` is given, the field's actual value is read from it via
    ``getattr``; otherwise the class-level default is used.

    Exactly one of primitive_type / nested_type will be set.
    """
    optional = False
    raw_type = field.type
    name = f"{parent_name}:{field.name}"
    value = getattr(instance, field.name) if instance is not None else field.default

    if get_origin(raw_type) is Union:
        args = get_args(raw_type)
        if type(None) in args:
            optional = True
            args = [a for a in args if a is not type(None)]

        dc_args = [a for a in args if dataclasses.is_dataclass(a)]
        if dc_args:
            return ResolvedField(
                name=name,
                optional=optional,
                value=value,
                hint=dc_args[0].__doc__,
                primitive_type=None,
                nested_type=dc_args[0],
            )

        for priority_type in FIELD_TYPE_MAPPING:
            if priority_type in args:
                return ResolvedField(
                    name=name,
                    optional=optional,
                    value=value,
                    hint="",
                    primitive_type=priority_type,
                    nested_type=None,
                )

        return None

    elif dataclasses.is_dataclass(raw_type):
        return ResolvedField(
            name=name,
            optional=optional,
            value=value,
            hint=raw_type.__doc__,
            primitive_type=None,
            nested_type=raw_type,
        )

    elif raw_type in FIELD_TYPE_MAPPING:
        return ResolvedField(
            name=name,
            optional=optional,
            value=value,
            hint="",
            primitive_type=raw_type,
            nested_type=None,
        )

    raise TypeError(
        f"No matching type found in FIELD_TYPE_MAPPING for field '{field.name}' "
        f"with type {field.type!r}"
    )


def extract_form_data(form_content):
    result = {}
    for item in form_content:
        item_id = item["props"]["id"]
        if (
            isinstance(item_id, dict)
            and item_id.get("type") == "growing-list-fieldset"
        ):
            # Growing list: InputWrapper(id=wrapper_id) > Stack(id=stack_id) > [inputs..., button_group]
            field_name = item_id["owner"].split(":")[-1]
            stack_children = item["props"]["children"]["props"]["children"]
            result[field_name] = [
                c["props"]["value"]
                for c in stack_children
                if "value" in c["props"] and c["props"]["value"] not in ("", None)
            ]
        elif item.get("type") == "Fieldset":
            field_name = item_id.split(":")[-1]
            result[field_name] = extract_form_data(item["props"]["children"])
        else:
            field_name = item_id.split(":")[1]
            result[field_name] = item["props"]["value"]
    return result


def disable_all_fields_dash_form(form):
    for i, t in enumerate(form):
        form[i]["props"]["disabled"] = True
    return form


def clean_field_name(field: str):
    return field.replace("_", " ").title()


def render_field_input(resolved: ResolvedField, disabled: bool = False):
    build_fn, icon = FIELD_TYPE_MAPPING[resolved.primitive_type]
    return build_fn(resolved, icon, disabled)


def validate_form(state):
    for item in state:
        item_type = item.get("type")
        if item_type == "Fieldset":
            if not validate_form(item["props"]["children"]):
                return False
        elif item_type == "InputWrapper":
            # GrowingList wrapper — no value prop; individual inputs validate themselves
            pass
        elif item["props"].get("required") and not item["props"].get("value"):
            return False
    return True


def add_space_between_capitals(s: str) -> str:
    label = re.sub(r"(?<!^)(?=[A-Z])", " ", s)
    label = label.replace("P S F", "PSF")
    return label


def render_fieldset(
    mm_dataclass,
    disabled: bool = False,
    form_id: str = "form_content",
    add_border: bool = False,
    background_level: int = 2,
) -> dmc.Fieldset:
    is_instance = not isinstance(mm_dataclass, type)
    children = []
    for field in fields(mm_dataclass):
        resolved = resolve_field_type(
            field, instance=mm_dataclass if is_instance else None
        )
        if resolved is None:
            continue
        if resolved.nested_type is not None:
            nested = (
                resolved.value
                if is_instance and resolved.value is not None
                else resolved.nested_type
            )
            children.append(
                render_fieldset(
                    mm_dataclass=nested,
                    disabled=disabled,
                    form_id=f"{form_id}:{field.name}",
                    add_border=True,
                    background_level=min(background_level + 1, 10),
                )
            )
        else:
            children.append(render_field_input(resolved, disabled=disabled))

    return dmc.Fieldset(
        id=form_id,
        children=children,
        # TODO: rely on the title of the class instead of class_name
        legend=dmc.Text(
            add_space_between_capitals(mm_dataclass.class_name),
            fw=700,
            fz="md",
        ),
        mt="lg",
        ml="xl",
        style=(
            {
                "backgroundColor": f"var(--mantine-color-gray-{background_level})",
                "borderTop": f"3px solid var(--mantine-color-gray-{background_level + 2})",
                "borderLeft": f"6px solid var(--mantine-color-gray-{background_level + 2})",
                "paddingLeft": "16px",
            }
            if add_border
            else {}
        ),
        variant="filled",
        radius="lg",
    )
