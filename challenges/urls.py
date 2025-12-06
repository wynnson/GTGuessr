from django.urls import path
from . import views

urlpatterns = [
    path("report/<int:challenge_id>/", views.report_challenge, name="challenges.report"),
    path("upload/", views.upload_image, name="challenges.upload"),
    path("image/<int:challenge_id>/", views.serve_converted_image, name="challenges.image"),
]