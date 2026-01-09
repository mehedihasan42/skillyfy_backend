from django.db import models
from users.models import User
from courses.models import Lesson,Course

# Create your models here.
class Quiz(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    lesson = models.ForeignKey(Lesson,on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz,related_name='questions',on_delete=models.CASCADE)    
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text
    

class Option(models.Model):
    question = models.ForeignKey(Question,related_name='options',on_delete=models.CASCADE) 
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def save(self,*args,**kwargs):
        if self.is_correct:
            Option.objects.filter(
                question = self.question,
                is_correct = True
            ).update(is_correct=False)
        super.save(*args,**kwargs)

    def __str__(self):
        return self.text    


class UserAnswer(models.Model):
    student = models.ForeignKey(User,on_delete=models.CASCADE)
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option,on_delete=models.CASCADE)
    answer_at = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     unique_together = ('user', 'question')

    def is_correct(self):
        return self.selected_option.is_correct