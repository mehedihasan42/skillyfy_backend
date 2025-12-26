from django.shortcuts import render
from . import models,serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

# Create your views here.
@api_view(['GET','POST'])
def category_list(request):
    if request.method == 'GET':
        categories = models.Category.objects.all()
        serializer = serializers.CategorySerializer(categories,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    if not request.user.is_authenticated or request.user.role != 'admin':
        return Response('Forbidden access',status=status.HTTP_403_FORBIDDEN)
    serializer = serializers.CategorySerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','POST'])
def course_list(request):
    if request.method == 'GET':
        category = request.query_params.get('category')
        search = request.query_params.get('search')
        queryset = models.Course.objects.all()

        if category:
            queryset = queryset.filter(category__name=category)

        if search:
            queryset = queryset.filter(
               Q(title__icontains = search) |
               Q(description__icontains = search)
            )    

        if request.user.is_authenticated or request.user.role == 'teacher':
            queryset = queryset.filter(instructor = request.user)  

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_queryset = paginator.paginate_queryset(queryset,request)

        serializer = serializers.CourseSerializer(
            paginated_queryset,
            many = True,
            context = {'request':request}
        )
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'admin':
            return Response({'details':'Only teacher can create courses'})
        serializer = serializers.CourseSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','POST'])
def lesson_list_create(request):
   if request.method == 'GET':
        course = request.query_params.get('courseId')

        if not course:
            return Response({'details':"You don't have access for this course"})
        
        try:
            course = models.Course.objects.get(pk=course)
        except models.Course.DoesNotExist:
            return Response({'details':"this course doesn't exits"})    

        is_teacher = request.user.is_authenticated and request.user.role == 'teacher' and request.user == course.instructor
        is_admin =  request.user.is_authenticated and request.user.role == 'admin'
        is_enrolled = models.Enrollment(
            student = request.user,
            course = course,
            status = 'active'
        ).exists() if request.user.is_authenticated and request.user.role == 'student' else False

        if not (is_admin or is_teacher or is_enrolled):
            return Response({'details':'You do not have permission for visit this page'})
        
        lesson = models.Lesson.objects.filter(course=course)
        serializer = serializers.LessonSerializer(lesson,many=True)
        return Response(serializer.data)
   
   elif request.method == 'POST':
        course = request.query_params.get('courseId')

        if not course:
            return Response({'details':"You don't have access for this course"})
        
        try:
            course = models.Course.objects.get(pk=course)
        except models.Course.DoesNotExist:
            return Response({'details':"this course doesn't exits"}) 

        if request.user != course.instructor:
            return Response({'details':'You can add lessons on your own courses'})   

        serializer = serializers.LessonSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['GET','POST'])
def material_list_create(request):
   if request.method == 'GET':
        lesson = request.query_params.get('lessonId')

        if not lesson:
            return Response({'details':"You don't have access for this course/lesson"})
        
        try:
            lesson = models.Lesson.objects.get(pk=lesson)
        except models.Lesson.DoesNotExist:
            return Response({'details':"this lesson doesn't exits"})    

        course = lesson.course
        is_teacher = request.user.is_authenticated and request.user.role == 'teacher' and request.user == course.instructor
        is_admin =  request.user.is_authenticated and request.user.role == 'admin'
        is_enrolled = models.Enrollment(
            student = request.user,
            course = course,
            status = 'active'
        ).exists() if request.user.is_authenticated and request.user.role == 'student' else False

        if not (is_admin or is_teacher or is_enrolled):
            return Response({'details':'You do not have permission for visit this page'})
        
        material = models.Material.objects.filter(course=course)
        serializer = serializers.MaterialSerializer(material,many=True)
        return Response(serializer.data)
   
   elif request.method == 'POST':
        lesson = request.query_params.get('lessonId')

        if not lesson:
            return Response({'details':"You don't have access for this lesson"})
        
        try:
            course = models.Lesson.objects.get(pk=lesson)
        except models.Lesson.DoesNotExist:
            return Response({'details':"this lesson doesn't exits"}) 

        if request.user != course.instructor:
            return Response({'details':'You can add lessons on your own courses'})   

        serializer = serializers.MaterialSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
   