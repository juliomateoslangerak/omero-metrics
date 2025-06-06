from django import forms
from dataclasses import fields
from microscopemetrics_schema import datamodel as mm_schema


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    dataset_id = forms.IntegerField(required=True)
    file = forms.FileField()


# TODO: Can we remove this?


def dataclass_to_form(dataclass):
    form_fields = {}
    for field in fields(dataclass):
        if field.type == str:
            form_fields[field.name] = forms.CharField(max_length=100)
        elif field.type == int:
            form_fields[field.name] = forms.IntegerField()
        elif field.type == float:
            form_fields[field.name] = forms.FloatField()
        elif field.type == bool:
            form_fields[field.name] = forms.BooleanField(required=False)

    return type(f"{dataclass.__name__}Form", (forms.Form,), form_fields)


# Usage:
ConfigForm = dataclass_to_form(mm_schema.FieldIlluminationInputParameters)
