from django.contrib import admin
from django.urls import path
from .views import *


urlpatterns = [
    path('category/', CategoryList.as_view(),name="category_list"),
    path('cards/', CourseListCreateApiView.as_view(),name="course_list"),
    path('<int:pk>/', CourseDetailApiView.as_view(), name='course-detail'),
    path('lesson/', lesson_list_create,name="lesson_list_create"),
    path('material/', material_list_create,name="material_list_create"),
    path('enrollment/', enrollment_list,name="enrollment_list"),
    path('enrollCourse/', enroll_course,name="enroll_course"),
    path('buy-course/<int:course_id>/', buy_course, name='buy_course'),
    path('payment_success/', payment_success, name='payment_success'),
    path('payment_fail/', payment_fail, name='payment_fail'),
    path('payment_cancel/', payment_cancel, name='payment_cancel'),
    path('is_enrolled/<int:course_id>/', is_enrolled, name='is_enrolled'),
]
