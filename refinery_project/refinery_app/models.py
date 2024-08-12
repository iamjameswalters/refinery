from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse_lazy

from pible import Bible

TRANSLATIONS = {"ESV": "English Standard Version", "KJV": "King James Version"}

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
    title = models.CharField(
        choices={book._title: book._title for book in Bible().books}, max_length=50
    )
    completed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse_lazy("home")


class Verse(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    book = models.CharField(
        choices={book._title: book._title for book in Bible().books}, max_length=50
    )
    chapter = models.SmallIntegerField()
    verse_number = models.SmallIntegerField()
    days_reviewed = models.SmallIntegerField(default=1)

    def __str__(self):
        return f"{self.book.title} {self.chapter}:{self.verse_number}"

    def get_verse(self):
        bible = Bible(
            translation=self.plan.translation,
            api_key=self.plan.api_key if self.plan.translation == "ESV" else None,
        )
        return bible[self.book][self.chapter][self.verse_number]
