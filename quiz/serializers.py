from rest_framework import serializers
from . import models


class OptionSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Option
        fields = ['id','text']

class QuestionSerializers(serializers.ModelSerializer):
    options = OptionSerializers(many=True)
    class Meta:
        model = models.Question
        fields = ['id','text','options']

class QuizSerializers(serializers.ModelSerializer):
    questions = QuestionSerializers(many=True)
    class Meta:
        model = models.Quiz
        fields = ['id','title','description','questions']

class UserAnswerSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.UserAnswer
        fields = ['question','selected_option']