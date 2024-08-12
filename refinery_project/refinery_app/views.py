from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView

from pible import Bible

from . import forms, models


def getPlan():
    return models.Plan.objects.first()


# Create your views here.


class HomePage(TemplateView):
    template_name = "refinery/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["plan"] = getPlan() or None
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
        plan = getPlan()
        self.object = models.Book.objects.create(
            title=form.cleaned_data["title"], plan=plan
        )
        plan.current_book = self.object
        plan.save()
        return redirect(self.get_success_url())


def previous_verses(request):
    plan = getPlan()
    yesterdays_verses = models.Verse.objects.filter(days_reviewed=1)
    if len(yesterdays_verses) == 0:
        return redirect("next_verses")

    verses = "<br />".join(
        f"{verse.chapter}:{verse.verse_number} {verse.get_verse()}"
        for verse in yesterdays_verses
    )

    if (
        len(
            models.Verse.objects.filter(
                days_reviewed__lt=plan.days_of_review, days_reviewed__gt=1
            )
        )
        > 0
    ):
        next_page = "review_verses"
    else:
        next_page = "next_verses"
    return render(
        request, "refinery/prev_verses.html", {"verses": verses, "next_page": next_page}
    )


def review_verses(request):
    plan = getPlan()

    more_than_one = models.Verse.objects.filter(days_reviewed__gt=1)
    if not len(more_than_one):
        for verse in models.Verse.objects.all():
            verse.days_reviewed += 1
            verse.save()
        return redirect("next_verses")

    review_verses = models.Verse.objects.filter(days_reviewed__lt=plan.days_of_review)
    match request.method:
        case "GET":
            verses = []
            for verse in review_verses:
                if len(verses) == 0:
                    verses.append(
                        {"title": verse.book.title(), "start": None, "end": None}
                    )
                if verses[-1]["title"] != verse.book.title():
                    verses.append(
                        {"title": verse.book.title(), "start": None, "end": None}
                    )
                if not verses[-1]["start"]:
                    verses[-1]["start"] = f"{verse.chapter}:{verse.verse_number}"
                else:
                    verses[-1]["end"] = f"{verse.chapter}:{verse.verse_number}"
            return render(request, "refinery/review_verses.html", {"verses": verses})
        case "POST":
            for verse in review_verses:
                verse.days_reviewed += 1
                verse.save()
            return redirect("next_verses")


def next_verses(request):
    plan = getPlan()
    current_book = plan.get_current_book()
    try:
        next_verse = (
            models.Verse.objects.filter(book=current_book.title)
            .last()
            .get_verse()
            .next_verse()
        )
    except AttributeError:
        next_verse = Bible(translation=plan.translation, api_key=plan.api_key)[
            current_book.title
        ][1][1]
    if request.method == "POST":
        models.Verse.objects.create(
            plan=plan,
            book=next_verse._book_title,
            chapter=next_verse._chapter_number,
            verse_number=next_verse.verse_number,
        )
        if len(models.Verse.objects.filter(days_reviewed=1)) >= plan.verses_per_day:
            return redirect("end_of_day")
        next_verse = next_verse.next_verse()
        print(next_verse)
    if not next_verse:
        current_book.completed = True
        current_book.save()
        return redirect("end_of_day")
    return render(request, "refinery/next_verses.html", {"verse": next_verse})


class EndOfDay(TemplateView):
    template_name = "refinery/end_of_day.html"
