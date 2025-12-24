from django.contrib import admin
from django.urls import path
from .views import category_list,course_list

urlpatterns = [
    path('category/', category_list,name="category_list"),
    path('cards/', course_list,name="course_list"),
]