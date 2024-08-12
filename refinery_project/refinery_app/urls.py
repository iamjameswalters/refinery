from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomePage.as_view(), name="home"),
    path("new-plan/", views.NewPlan.as_view(), name="new_plan"),
    path("new-book/", views.NewBook.as_view(), name="new_book"),
    path("plan/next-verses/", views.next_verses, name="next_verses"),
    path("plan/previous-verses/", views.previous_verses, name="prev_verses"),
    path("plan/review-verses/", views.review_verses, name="review_verses"),
    path("plan/end-of-day/", views.EndOfDay.as_view(), name="end_of_day"),
]
