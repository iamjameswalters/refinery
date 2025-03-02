from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse_lazy

from pible import Bible

TRANSLATIONS = {"ESV": "English Standard Version", "KJV": "King James Version"}

# Define the five books of Psalms
PSALMS_BOOKS = {
    "Psalms (Book 1)": (1, 41),
    "Psalms (Book 2)": (42, 72),
    "Psalms (Book 3)": (73, 89),
    "Psalms (Book 4)": (90, 106),
    "Psalms (Book 5)": (107, 150),
}


def get_book_choices():
    """
    Get book choices with the five books of Psalms instead of a single Psalms book.
    The five books of Psalms are placed in the correct biblical order, between Job and Proverbs.
    """
    bible = Bible()
    choices = {}

    # Get all books in biblical order
    bible_books = [book._title for book in bible.books]

    # Find the index of Psalms (should be between Job and Proverbs)
    psalms_index = bible_books.index("Psalms")

    # Add books before Psalms
    for i in range(psalms_index):
        book_title = bible_books[i]
        choices[book_title] = book_title

    # Add the five books of Psalms in order
    for psalms_book in sorted(PSALMS_BOOKS.keys()):
        choices[psalms_book] = psalms_book

    # Add books after Psalms
    for i in range(psalms_index + 1, len(bible_books)):
        book_title = bible_books[i]
        choices[book_title] = book_title

    return choices


# Create your models here.


class CustomUser(AbstractUser):
    # this is defined in case we need to add a user model to this later
    pass


class Plan(models.Model):
    verses_per_day = models.SmallIntegerField(choices=[(i, i) for i in range(1, 11)])
    days_of_review = models.SmallIntegerField(default=100)
    translation = models.CharField(choices=TRANSLATIONS, max_length=5)
    api_key = models.CharField(max_length=40, blank=True)

    def get_absolute_url(self):
        return reverse_lazy("home")

    def get_current_book(self):
        return self.book_set.get(completed=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(models.Q(translation="ESV") and ~models.Q(api_key=""))
                | ~models.Q(translation="ESV"),
                name="require_api_key_for_esv",
            )
        ]


class Book(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    title = models.CharField(choices=get_book_choices(), max_length=50)
    completed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse_lazy("home")


class Verse(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    book = models.CharField(choices=get_book_choices(), max_length=50)
    chapter = models.SmallIntegerField()
    verse_number = models.SmallIntegerField()
    days_reviewed = models.SmallIntegerField(default=1)

    def __str__(self):
        return f"{self.book} {self.chapter}:{self.verse_number}"

    def get_verse(self):
        bible = Bible(
            translation=self.plan.translation,
            api_key=self.plan.api_key if self.plan.translation == "ESV" else None,
        )

        # Handle the five books of Psalms
        if self.book.startswith("Psalms (Book "):
            # Extract the Psalms range
            psalms_range = PSALMS_BOOKS[self.book]

            # Check if the chapter is within the range for this book of Psalms
            if psalms_range[0] <= self.chapter <= psalms_range[1]:
                return bible["Psalms"][self.chapter][self.verse_number]
            else:
                raise ValueError(
                    f"Chapter {self.chapter} is out of range for {self.book}"
                )
        else:
            return bible[self.book][self.chapter][self.verse_number]
