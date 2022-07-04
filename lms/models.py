from email.policy import default
from django.db import models
import json

# Create your models here.
from django.contrib.auth.models import User

Roles=(
    ('Student','Student'),
    ('Instructor','Instructor'),
)

Status=(
    ('Not Submitted','Not Submitted'),
    ('Submitted','Submitted'),
    ('Checked','Checked'),
)

class Profile(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    Fname=models.CharField(max_length=50,blank=True,null=True)
    Lname=models.CharField(max_length=50,blank=True,null=True)
    role=models.CharField(max_length=10,choices=Roles,default="Student")
    coursesEnrolled=models.ManyToManyField('Course',related_name="Courses",blank=True)
    

class Course(models.Model):
    Instructor=models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    code=models.CharField(max_length=15)
    discription=models.TextField()
    image=models.FileField( upload_to="./image", null=True,blank=True)
    content=models.TextField(null=True,blank=True)
    totalMarks=models.DecimalField(default=0.0, max_digits=5, decimal_places=2)
    # using unique Constraints to ensure that one Instructor can create only one course with same course code
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Instructor', 'code'], name='unique_course')
        ]
    

class Progress(models.Model):
    Student=models.ForeignKey(User,on_delete=models.CASCADE)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    completionPercentage=models.DecimalField(max_digits=5,decimal_places=2,default=0.0)
    currMarks=models.DecimalField(max_digits=5,decimal_places=2,default=0.0)

class Quiz(models.Model):
    course=models.ForeignKey(Course,null=True,on_delete=models.CASCADE)
    name=models.CharField(max_length=200,null=True,blank=True)
    createdAt=models.DateTimeField(auto_now_add=True,null=True)
    totalMarks=models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    timeLimit=models.IntegerField(null=True,blank=True)
    

class Question(models.Model):
    quiz=models.ForeignKey(Quiz,null=True,on_delete=models.CASCADE)
    question=models.TextField(null=True,blank=True)
    answer=models.TextField(null=True,blank=True)
    maxMarks=models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    #we store options list in the form of string
    allOptions=models.TextField(null=True,blank=True)


class Result(models.Model):
    student=models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    quiz=models.ForeignKey(Quiz,null=True,on_delete=models.CASCADE)
    startTime=models.DateTimeField(null=True,blank=True)
    choosenOptions=models.TextField(null=True,blank=True)
    marks=models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    # Added Unique Constraint so that student can submit the quiz only once
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'quiz'], name='unique_submission')
        ]







