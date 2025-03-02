from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView

from pible import Bible

from . import forms, models
from .models import PSALMS_BOOKS


def getPlan():
    return models.Plan.objects.first()


def get_next_verse_for_psalms_book(current_verse, book_title, bible):
    """
    Get the next verse for a Psalms book, respecting the boundaries of each book.
    """
    # Get the range for this Psalms book
    start_chapter, end_chapter = PSALMS_BOOKS[book_title]

    # Try to get the next verse
    try:
        next_verse = current_verse.next_verse()

        # Check if the next verse is still within the range for this book
        if next_verse and next_verse._chapter_number <= end_chapter:
            return next_verse
        else:
            # We've reached the end of this Psalms book
            return None
    except AttributeError:
        # If there's an error getting the next verse, try to get the first verse
        if book_title.startswith("Psalms (Book "):
            return bible["Psalms"][start_chapter][1]
        else:
            return bible[book_title][1][1]


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
    yesterdays_verses = models.Verse.objects.filter(days_reviewed=1)
    if len(yesterdays_verses) == 0:
        return redirect("next_verses")

    verses = "<br />".join(
        f"{verse.chapter}:{verse.verse_number} {verse.get_verse()}"
        for verse in yesterdays_verses
    )

    return render(request, "refinery/prev_verses.html", {"verses": verses})


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
                    verses.append({"title": verse.book, "start": None, "end": None})
                if verses[-1]["title"] != verse.book:
                    verses.append({"title": verse.book, "start": None, "end": None})
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
    bible = Bible(
        translation=plan.translation,
        api_key=plan.api_key if plan.translation == "ESV" else None,
    )

    # Check if we're working with a Psalms book
    is_psalms_book = current_book.title.startswith("Psalms (Book ")

    try:
        last_verse = models.Verse.objects.filter(book=current_book.title).last()
        if last_verse:
            current_verse = last_verse.get_verse()

            # Get the next verse, handling Psalms books specially
            if is_psalms_book:
                next_verse = get_next_verse_for_psalms_book(
                    current_verse, current_book.title, bible
                )
            else:
                next_verse = current_verse.next_verse()
        else:
            # No verses yet, get the first verse
            if is_psalms_book:
                # Get the first chapter for this Psalms book
                start_chapter, _ = PSALMS_BOOKS[current_book.title]
                next_verse = bible["Psalms"][start_chapter][1]
            else:
                next_verse = bible[current_book.title][1][1]
    except AttributeError:
        # Fallback to get the first verse
        if is_psalms_book:
            # Get the first chapter for this Psalms book
            start_chapter, _ = PSALMS_BOOKS[current_book.title]
            next_verse = bible["Psalms"][start_chapter][1]
        else:
            next_verse = bible[current_book.title][1][1]

    if request.method == "POST":
        # Create a new verse
        if is_psalms_book:
            # For Psalms books, we need to store the custom book title
            models.Verse.objects.create(
                plan=plan,
                book=current_book.title,  # Use the custom Psalms book title
                chapter=next_verse._chapter_number,
                verse_number=next_verse.verse_number,
            )
        else:
            models.Verse.objects.create(
                plan=plan,
                book=next_verse._book_title,
                chapter=next_verse._chapter_number,
                verse_number=next_verse.verse_number,
            )

        if len(models.Verse.objects.filter(days_reviewed=1)) >= plan.verses_per_day:
            return redirect("end_of_day")

        # Get the next verse for the next iteration
        if is_psalms_book:
            next_verse = get_next_verse_for_psalms_book(
                next_verse, current_book.title, bible
            )
        else:
            next_verse = next_verse.next_verse()

    if not next_verse:
        current_book.completed = True
        current_book.save()
        return redirect("end_of_day")

    return render(request, "refinery/next_verses.html", {"verse": next_verse})


class EndOfDay(TemplateView):
    template_name = "refinery/end_of_day.html"
