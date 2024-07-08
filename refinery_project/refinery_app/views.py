from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, CreateView

from . import forms, models

# Create your views here.

class HomePage(TemplateView):
    template_name = "refinery/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_plan = models.Plan.objects.first()
        if current_plan:
            context["plan"] = current_plan
        return context
    

class NewPlan(CreateView):
    template_name = "refinery/new_plan.html"    
    model = models.Plan
    form_class = forms.PlanForm
    