from django.urls import path

from . import views

urlpatterns = [
    path('', views.POSTS.as_view()),
    path('categories/', views.CATEGORIES.as_view()),
    path('<int:post_id>/', views.POSTS.as_view()),
    path('<int:post_id>/questions/', views.QUESTIONS.as_view()),
    path('<int:post_id>/questions/<int:question_id>/', views.QUESTIONS.as_view()),
    path('<int:post_id>/questions/<int:question_id>/replies/', views.REPLIES.as_view()),
    path('<int:post_id>/questions/<int:question_id>/replies/<int:reply_id>/', views.REPLIES.as_view()),
]