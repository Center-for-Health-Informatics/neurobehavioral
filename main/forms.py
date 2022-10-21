from django import forms
from . import models


class InstrumentCreationRuleForm(forms.ModelForm):

    # def __init__(self, user, *args, **kwargs):
    #     super(InstrumentCreationRuleForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.InstrumentCreationRule
        fields = '__all__'
        # exclude = ['title']

        widgets = {
            'instruments': forms.SelectMultiple(attrs={'size': 10}),
        }
