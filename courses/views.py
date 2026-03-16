from django.shortcuts import render
from . import models,serializers
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
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
from rest_framework.permissions import BasePermission,AllowAny,SAFE_METHODS

# Create your views here.
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'   

class CategoryList(ListCreateAPIView):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [AllowAny()]

class CourseListPagination(PageNumberPagination):
    page_size = 10

class CourseListCreateApiView(ListCreateAPIView):
    serializer_class = serializers.CourseSerializer
    authentication_classes = [JWTAuthentication]
    pagination_class = CourseListPagination

    def get_queryset(self):
        request = self.request
        queryset = models.Course.objects.all()
        category = request.query_params.get('category')
        search = request.query_params.get('search')

        if category:
            queryset = queryset.filter(category_id = category)

        if search:
            queryset = queryset.filter(
                Q(title__icontains = search) |
                Q(description__icontains = search)
            )    

        if request.user.is_authenticated and request.user.role == 'teacher':
            queryset = queryset.filter(instructor=request.user)

        return queryset
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [AllowAny()]

class CourseDetailApiView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CourseSerializer
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return models.Course.objects.all()

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdmin()]
        return [AllowAny()]
    

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
    print('Your trns id is: ',tran_id)

    ssl_data = {
        'store_id': settings.SSLCOMMERZE_STORE_ID,
        'store_passwd': settings.SSLCOMMERZE_STORE_PASSWORD,
        'currency': 'BDT',
        'product_name': course.title,
        'cus_name': request.user.username,
        'cus_email': request.user.email,
        "tran_id": tran_id,
        "total_amount": course.price,
        "success_url": "https://skillyfy-backend.onrender.com/course/payment_success/",
        "fail_url": "https://skillyfy-backend.onrender.com/course/payment_fail/",
        "cancel_url": "https://skillyfy-backend.onrender.com/course/payment_cancel/",
    }

    response = requests.post(settings.SSLCOMMERZE_PAYMENT_URL, data=ssl_data)
    response_data = response.json()

    return Response({
        "payment_url": response_data['GatewayPageURL']
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def payment_success(request):

    print("DATA RECEIVED:", request.data)

    tran_id = request.data.get('tran_id')  

    if not tran_id:
        return Response({"error": "tran_id missing"}, status=400)

    try:
        payment = models.Payment.objects.get(tran_id=tran_id)
    except models.Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)

    payment.status = 'success'
    payment.save()

    enrollment_exist = models.Enrollment.objects.filter(
        student=payment.student,
        course=payment.course
    ).exists()   

    if not enrollment_exist:
        models.Enrollment.objects.create(
            student=payment.student,
            course=payment.course,
            price=payment.amount
        )

    return redirect(
        f"https://skillyfy-learning.netlify.app/payment-success?tran_id={tran_id}"
    )



@api_view(['POST'])
@permission_classes([AllowAny])
def payment_fail(request):
    tran_id = request.data.get('tran_id')
    models.Payment.objects.filter(tran_id=tran_id).update(status='fail')
    return redirect(f"https://skillyfy-learning.netlify.app/payment_fail")


@api_view(['POST'])
@permission_classes([AllowAny])
def payment_cancel(request):
    tran_id = request.data.get('tran_id')
    models.Payment.objects.filter(tran_id=tran_id).update(status='cancel')
    return redirect(f"https://skillyfy-learning.netlify.app/payment_cancel")


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
       

@api_view(['GET'])
def is_enrolled(request,course_id):
    if request.user.role != 'student':
        return Response({'details':'Only students can enroll'},status=status.HTTP_403_FORBIDDEN)
    
    enrolled = models.Enrollment.objects.filter(
        student = request.user,
        course_id = course_id,
        is_active = True
    ).exists()

    if enrolled:
        return Response({'enrolled':True},status=status.HTTP_200_OK)
    else:
        return Response({'enrolled':False},status=status.HTTP_200_OK)