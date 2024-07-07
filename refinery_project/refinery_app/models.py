from django.db import models
from django.contrib.auth.models import AbstractUser

from pible import Bible

TRANSLATIONS = {"ESV": "English Standard Version", "KJV": "King James Version"}

# Create your models here.


class CustomUser(AbstractUser):
    # this is defined in case we need to add a user model to this later
    pass


class Plan(models.Model):
    current_book = models.ForeignKey("Book", on_delete=models.RESTRICT)
    current_verse = models.ForeignKey("Verse", on_delete=models.RESTRICT)
    verses_per_day = models.SmallIntegerField(choices=[(i, i) for i in range(1, 11)])
    days_of_review = models.SmallIntegerField(default=100)
    translation = models.CharField(choices=TRANSLATIONS)
    api_key = models.CharField(max_length=40, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(translation="ESV", api_key__isnull=False)
                | ~models.Q(translation="ESV"),
                name="require_api_key_for_esv",
            )
        ]


class Book(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    title = models.CharField(choices={book: book for book in Bible().books})
    completed = models.BooleanField(default=False)


class Verse(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    book = models.CharField(choices={book: book for book in Bible().books})
    chapter = models.SmallIntegerField()
    verse_number = models.SmallIntegerField()
    days_reviewed = models.SmallIntegerField(default=1)
