from django.db import models
from users.models import User

# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    banner = models.ImageField(upload_to='media/course_banners/')
    price = models.FloatField()
    duration = models.FloatField()
    is_active = models.BooleanField()
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='course')
    instructor = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    video = models.FileField(upload_to='media/video_lessons/')
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='lesson')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Material(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    file_type = models.CharField(max_length=50)
    file = models.FileField(upload_to='media/materials/')
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='lesson')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Enrollment(models.Model):
    student = models.ForeignKey(User,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    price = models.FloatField()
    progress = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    total_mark = models.FloatField(default=0)
    is_certificate_ready = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.student.username} - {self.course.title}'
    

class QuestionAndAns(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson,on_delete=models.CASCADE)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.lesson.title}'