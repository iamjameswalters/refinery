from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomePage.as_view(), name="home"),
    path("new-plan/", views.NewPlan.as_view(), name="new_plan"),
    path("new-book/", views.NewBook.as_view(), name="new_book"),
]