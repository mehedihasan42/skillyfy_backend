from django.urls import path
from . import views

urlpatterns = [
    path("<int:lesson_id>/quizzes/", views.quizzes_by_lesson),
    path('submit/', views.submit_answer),
    path('result/<int:quiz_id>/', views.quiz_result),
]
