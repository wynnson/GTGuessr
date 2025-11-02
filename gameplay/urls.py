from django.urls import path
from . import views

urlpatterns = [
    path("start/", views.start_play, name="gameplay.start"),
    path("<int:challenge_id>/", views.play, name="gameplay.play"),
    path("result/<int:guess_id>/", views.result, name="gameplay.result"),
]
