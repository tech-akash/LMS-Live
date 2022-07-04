
from dataclasses import fields
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Progress,Course,Quiz,Question,Result
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['username','password','email']
    def create(self, validated_data):
        user=User.objects.create(username=validated_data['username'],email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Course
        fields=['name','Instructor','discription','code','image']

class CourseSerializer(serializers.ModelSerializer):
    Instructor=serializers.SerializerMethodField()
    class Meta:
        model=Course
        fields=['id','name','Instructor','code','discription','totalMarks','image']
    def get_Instructor(self,obj):
        return obj.Instructor.username

class DashboardSerializer(serializers.ModelSerializer):
    course=CourseSerializer()
    class Meta:
        model=Progress
        fields=['course','currMarks']

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model=Quiz
        fields=['name','totalMarks','timeLimit','course']

class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields=['id','question','answer','maxMarks','quiz','allOptions']

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model=Result
        fields=['student','quiz','choosenOptions','marks']

class ProfileSerializer(serializers.ModelSerializer):
    coursesEnrolled=CourseSerializer(many=True)
    class Meta:
        model=Profile
        fields=['user','role','Fname','Lname','coursesEnrolled']