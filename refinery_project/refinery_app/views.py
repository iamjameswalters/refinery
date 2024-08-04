from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, CreateView, UpdateView

from . import forms, models

# Create your views here.

class HomePage(TemplateView):
    template_name = "refinery/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_plan = models.Plan.objects.first()
        if current_plan:
            context["plan"] = current_plan
        else:
            context["plan"] = None
        return context
    

class NewPlan(CreateView):
    template_name = "refinery/new_plan.html"    
    model = models.Plan
    form_class = forms.PlanForm
    
class NewBook(CreateView):
    template_name = "refinery/new_book.html"
    model = models.Book
    form_class = forms.BookForm

    def form_valid(self, form):
        plan = models.Plan.objects.first()
        self.object = models.Book(
            title=form.cleaned_data["title"], 
            plan=plan
        )
        self.object.save()
        plan.current_book = self.object
        plan.save()
        return HttpResponseRedirect(self.get_success_url())

class NextVerse(TemplateView):
    ...

class ReviewVerses(TemplateView):
    ...