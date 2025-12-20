from . import models
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['title','is_active']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        exclude = ('created_at','updated_at')     

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lesson
        exclude = ('created_at','updated_at')      

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Material
        exclude = ('created_at','updated_at')  

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Enrollment
        exclude = ('created_at','updated_at')

class QuestionAndAnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuestionAndAns
        exclude = ('created_at','updated_at')            