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


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        login(request,user)
        return Response({'details':'User register successfull'},status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username,password=password)

    if user is not None:
        login(request,user)
        return Response({'message':'Login successfull','user_id':user.id,'username':user.username,'email':user.email})
    
    return Response({'error':'Invalid User'},status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def profile(request):
    return Response({'username':request.user.username,'email':request.user.email})