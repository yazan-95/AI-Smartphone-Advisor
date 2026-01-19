from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("recommend/", views.recommend, name="recommend"),  # NO /api/
    path("3d-status/<str:model_slug>/", views.check_3d_status, name="check_3d_status"),  # NO /api/
]
