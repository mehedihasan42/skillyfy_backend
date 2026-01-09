from django.shortcuts import render
from . import models,serializers
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import uuid
from django.conf import settings
import requests
from django.shortcuts import redirect

# Create your views here.
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])   # 👈 allow GET without token
def category_list(request):

    if request.method == 'GET':
        categories = models.Category.objects.all()
        serializer = serializers.CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 🔐 POST requires authentication
    if not request.user.is_authenticated or request.user.role != 'admin':
        return Response(
            {'detail': 'Forbidden access'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = serializers.CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def course_list(request):

    if request.method == 'GET':
        category = request.query_params.get('category')
        search = request.query_params.get('search')
        queryset = models.Course.objects.all()

        if category:
            queryset = queryset.filter(category__name=category)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        if request.user.role == 'teacher':
            queryset = queryset.filter(instructor=request.user)   

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = serializers.CourseSerializer(
            paginated_queryset,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    elif request.method == 'POST':
        if request.user.role != 'teacher':
            return Response(
                {'detail': 'Only teacher can create courses'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = serializers.CourseSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save(instructor=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def course_detail(request,pk):
    course = get_object_or_404(models.Course,pk=pk)

    if request.user.role == 'teacher' and course.instructor != request.user:
       return Response({'details':'You dont have access to see this course'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = serializers.CourseSerializer(course,context={'request':request})

    return Response(serializer.data,status=status.HTTP_200_OK)
    

@api_view(['GET','POST'])
def lesson_list_create(request):
   if request.method == 'GET':
        course = request.query_params.get('courseId')
        print('course id: ',course)

        if not course:
            return Response({'details':"You don't have access for this course"})
        
        try:
            course = models.Course.objects.get(pk=course)
        except models.Course.DoesNotExist:
            return Response({'details':"this course doesn't exits"})    

        is_teacher = request.user.is_authenticated and request.user.role == 'teacher' and request.user == course.instructor
        is_admin =  request.user.is_authenticated and request.user.role == 'admin'
        is_enrolled = models.Enrollment.objects.filter(
        student=request.user,
        course=course,
        is_active=True
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
        course = request.query_params.get('courseId')
        print('course id: ',course)

        if not course:
            return Response({'details':"You don't have access for this course"})
        
        try:
            course = models.Course.objects.get(pk=course)
        except models.Course.DoesNotExist:
            return Response({'details':"this course doesn't exits"})    

        is_teacher = request.user.is_authenticated and request.user.role == 'teacher' and request.user == course.instructor
        is_admin =  request.user.is_authenticated and request.user.role == 'admin'
        is_enrolled = models.Enrollment.objects.filter(
        student=request.user,
        course=course,
        is_active=True
         ).exists() if request.user.is_authenticated and request.user.role == 'student' else False


        if not (is_admin or is_teacher or is_enrolled):
            return Response({'details':'You do not have permission for visit this page'})
        
        lesson = models.Material.objects.filter(course=course)
        serializer = serializers.MaterialSerializer(lesson,many=True)
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


@api_view(['GET'])
def enrollment_list(request):
    if request.method == 'GET':
            course = request.query_params.get('courseId')

            if not course:
                return Response({'details':"You don't have access for this course"})
            
            try:
                course = models.Course.objects.get(pk=course)
            except models.Course.DoesNotExist:
                return Response({'details':"this course doesn't exits"})   
            if request.user.role == 'teacher':
                    if request.user != course.instructor:
                        return Response({'details':"You can't see this course enrollment information"})
                    
                    enrollments = models.Enrollment.objects.filter(course=course)
                    serializer = serializers.EnrollmentSerializer(enrollments,many=True)
                    return Response(serializer.data)
            elif request.user.role == 'student':    
                    enrollments = models.Enrollment.objects.filter(student=request.user)
                    serializer = serializers.EnrollmentSerializer(enrollments,many=True)
                    return Response(serializer.data)
            elif request.user.role == 'admin':
                    enrollments = models.Enrollment.objects.filter(course=course)
                    serializer = serializers.EnrollmentSerializer(enrollments,many=True)
                    return Response(serializer.data)
            else:
                return Response({'details':'Unauthorized access'},status=status.HTTP_403_FORBIDDEN)
            

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_course(request,course_id):
    course = models.Course.objects.get(id=course_id)

    tran_id = str(uuid.uuid4())

    models.Payment.objects.create(
        student = request.user,
        course = course,
        tran_id = tran_id,
        amount = course.price,
        status = 'pendding'
    )

    ssl_data = {
        'store_id': settings.SSLCOMMERZE_STORE_ID,
        'store_passwd': settings.SSLCOMMERZE_STORE_PASSWORD,
        'currency': 'BDT',
        'product_name': course.title,
        'cus_name': request.user.username,
        'cus_email': request.user.email,
        "tran_id": tran_id,
        "total_amount": course.price,
        "success_url": "http://localhost:8000/course/payment_success/",
        "fail_url": "http://localhost:8000/course/payment_fail/",
        "cancel_url": "http://localhost:8000/course/payment_cancel/",
    }

    response = requests.post(settings.SSLCOMMERZE_PAYMENT_URL, data=ssl_data)
    response_data = response.json()

    return Response({
        "payment_url": response_data['GatewayPageURL']
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def payment_success(request):
    tran_id = request.data.get('tran_id')

    payment = models.Payment.objects.get(tran_id=tran_id)

    payment.status = 'success'
    payment.save()

    enrollment_exist = models.Enrollment.objects.filter(
        student = payment.student,
        course = payment.course
    )

    if not enrollment_exist:
        models.Enrollment.objects.create(
            student = payment.student,
            course = payment.course,
            price = payment.amount
        )

    return redirect(f"http://localhost:5173/payment-success?tran_id={tran_id}")


@api_view(['POST'])
@permission_classes([AllowAny])
def payment_fail(request):
    tran_id = request.data.get('tran_id')
    models.Payment.objects.filter(tran_id=tran_id).update(status='fail')
    return redirect(f"http://localhost:5173/payment_fail")


@api_view(['POST'])
@permission_classes([AllowAny])
def payment_cancel(request):
    tran_id = request.data.get('tran_id')
    models.Payment.objects.filter(tran_id=tran_id).update(status='cancel')
    return redirect(f"http://localhost:5173/payment_cancel")


@api_view(['GET','POST'])
def enroll_course(request):
   if request.method == 'POST':
        if request.user.role != 'student':
          return Response({'details':'only students or logged in user can enroll'})
    
        course = request.data.get('course')
        payment_method = request.data.get('payment_method','free')

        try:
            course = models.Course.objects.get(pk=course)
        except models.Course.DoesNotExist:
            return Response({'details':'course not found'})

        if models.Enrollment.objects.filter(student=request.user,course=course).exists():
            return Response({'detail':'you are already enrolled in this course'})    
        
        enrollment = models.Enrollment.objects.create(
            student = request.user,
            course = course,
            payment_method = payment_method,
            status = 'active'
        )
        serializer = serializers.EnrollmentSerializer(enrollment)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
   
   elif request.method == 'GET':
        enrollments = models.Enrollment.objects.filter(student=request.user)
        courses = [e.course for e in enrollments]
        serializer = serializers.CourseSerializer(courses, many=True) 
        return Response(serializer.data)
       

def is_enrolled(request,course_id):
    if request.user.role == 'student':
     if not models.Enrollment.objects.filter(
        student = request.user,
        course_id = course_id,
        is_active = True
      ).exists():
         return Response({'detail':'Forbidden access. You are not enrolled in this course'})