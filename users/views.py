from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer,RegisterSerializer
from django.contrib.auth import authenticate,login
from rest_framework import status

# Create your views here.
@api_view(['GET','POST'])
def user_list_create(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return Response({'Forbidden access'},status=401)
        if request.user.role == 'admin':
            user = User.objects.all()
        else:
            user = User.objects.filter(id=request.user.id) 
        serializer = UserSerializer(user,many=True)  
        return Response(serializer.data)  
    
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=400)


@api_view(['GET','POST'])
@permission_classes([AllowAny])
def register_view(request):

    if request.method == 'GET':
        return Response({
            "expected_fields": {
                "username": "string, required",
                "email": "string, required",
                "role": "string, required (e.g., 'student', 'teacher')",
                "mobile_no": "string, required",
                "password": "string, required",
                "confirm_password": "string, required"
            }
        })

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        login(request,user)
        return Response({'details':'User register successfull'},status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error':'Email and password are required'},status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error':'Invalid email or password'},status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(username=user_obj.username,password=password)  

    if user is not None:
        login(request,user)
        return Response({'message':'Login successfull',
                         'user_id':user.id,
                         'username':user.username,
                         'email':user.email
                         },status=status.HTTP_200_OK)  
            
    return Response({'error':'Invalid User'},status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def profile(request):
    return Response({'username':request.user.username,'email':request.user.email})