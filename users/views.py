from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer,RegisterSerializer
from django.contrib.auth import authenticate,login
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

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

# ******************varify email by 4 digit code and forget password and reset password also***************

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_list(request):
    teachers = User.objects.filter(role='teacher')
    serializer = UserSerializer(teachers,many=True)
    return Response(serializer.data)

def get_tokens_for_user(user):
    refersh = RefreshToken.for_user(user)

    return {
        'refresh':str(refersh),
        'access':str(refersh.access_token)
    }

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
        tokens = get_tokens_for_user(user)
        return Response({
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }, status=status.HTTP_200_OK)
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
        tokens = get_tokens_for_user(user)
        return Response({
            'message': 'Login successful',
            'access':  tokens['access'],
            'refresh': tokens['refresh'],
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }, status=status.HTTP_200_OK)
            
    return Response({'error':'Invalid User'},status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def profile(request):
    return Response({'username':request.user.username,'email':request.user.email})
