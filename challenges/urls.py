from django.urls import path
from . import views

urlpatterns = [
    path("report/<int:challenge_id>/", views.report_challenge, name="challenges.report"),
    path("upload/", views.upload_image, name="challenges.upload"),
]