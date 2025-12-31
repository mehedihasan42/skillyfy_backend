from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
     model = User
     fields = (
            "id",
            "username",
            "email",
            "role",
            "mobile_no"
        )

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True) 
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
       model = User
       fields = (
            "username",
            "email",
            "role",
            "mobile_no",
            "password",
            "confirm_password"
        )

    def validate(self,data):
       if data['password'] != data['confirm_password']:
          raise serializers.ValidationError("Passwords do not match.")
       return data

    def create(self,validated_data):
       validated_data.pop('confirm_password')
       user = User.objects.create_user(**validated_data)
       return user    