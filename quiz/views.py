from django.shortcuts import render
from . import models,serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quizzes_by_lesson(request, lesson_id):
    quizzes = models.Quiz.objects.filter(lesson_id=lesson_id)
    serializer = serializers.QuizSerializers(quizzes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request):
    serializer = serializers.UserAnswerSerializers(data=request.data)

    if serializer.is_valid():
        models.UserAnswer.objects.update_or_create(
            student=request.user,
            question=serializer.validated_data['question'],
            defaults={
                'selected_option': serializer.validated_data['selected_option']
            }
        )
        return Response({'message': 'Answer saved'})
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_result(request, quiz_id):
    answers = models.UserAnswer.objects.filter(
        student=request.user,
        question__quiz_id=quiz_id
    )

    total = answers.count()
    correct = sum([1 for a in answers if a.is_correct()])

    return Response({
        'total_questions': total,
        'correct_answers': correct,
        'score': f"{correct}/{total}"
    })
