from django.urls import path

from . import views

urlpatterns = [
    path('modal/', views.CATCH_SLACK_COMMAND.as_view()),
    path('', views.POST_VIA_SLACK.as_view()),
]