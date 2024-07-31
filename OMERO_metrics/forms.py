from django import forms


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    dataset_id = forms.IntegerField(required=True)
    file = forms.FileField()
