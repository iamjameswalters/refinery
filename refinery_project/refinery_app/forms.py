from django import forms
from . import models


class PlanForm(forms.ModelForm):
    class Meta:
        model = models.Plan
        fields = ["translation", "api_key", "verses_per_day", "days_of_review"]


class BookForm(forms.ModelForm):
    class Meta:
        model = models.Book
        fields = [
            "title",
        ]
