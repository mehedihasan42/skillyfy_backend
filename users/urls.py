from django.contrib import admin
from django.urls import path
from .views import user_list_create,register_view,login_view,teacher_list

urlpatterns = [
    path('auth/', user_list_create,name="user_list_create"),
    path('register/', register_view,name="registar_view"),
    path('login/', login_view,name="login_view"),
    path('teacher_list/', teacher_list,name="teacher_list"),
]
