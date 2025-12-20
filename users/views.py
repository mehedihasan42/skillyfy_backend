from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer

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
``