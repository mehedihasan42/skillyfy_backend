from django.contrib import admin
from django.urls import path
from .views import category_list,course_list,lesson_list_create,material_list_create,enrollment_list,enroll_course,course_detail,buy_course,payment_success,payment_fail,payment_cancel,is_enrolled

urlpatterns = [
    path('category/', category_list,name="category_list"),
    path('cards/', course_list,name="course_list"),
    path('lesson/', lesson_list_create,name="lesson_list_create"),
    path('material/', material_list_create,name="material_list_create"),
    path('enrollment/', enrollment_list,name="enrollment_list"),
    path('enrollCourse/', enroll_course,name="enroll_course"),
    path('<int:pk>/', course_detail, name='course-detail'),
    path('buy-course/<int:course_id>/', buy_course, name='buy_course'),
    path('payment_success/', payment_success, name='payment_success'),
    path('payment_fail/', payment_fail, name='payment_fail'),
    path('payment_cancel/', payment_cancel, name='payment_cancel'),
    path('is_enrolled/<int:course_id>/', is_enrolled, name='is_enrolled'),
]
