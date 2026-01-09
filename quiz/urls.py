from django.urls import path
from . import views

urlpatterns = [
    path('<int:quiz_id>/', views.quiz_detail),
    path('submit/', views.submit_answer),
    path('result/<int:quiz_id>/', views.quiz_result),
]
