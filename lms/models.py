from email.policy import default
import string
from django.db import models
import json
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
    allowedAttempt=models.IntegerField(default=1)
    createdAt=models.DateTimeField(auto_now_add=True,null=True)
    totalMarks=models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    timeLimit=models.IntegerField(default=20)
    def clean(self):
        if self.timeLimit<=0:
            raise ValidationError("Time Limit must be a positve number")

class Question(models.Model):
    quiz=models.ForeignKey(Quiz,null=True,on_delete=models.CASCADE)
    question=models.TextField(null=True,blank=True)
    answer=models.TextField(null=True,blank=True)
    maxMarks=models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    #we store options list in the form of string
    allOptions=models.TextField(null=True,blank=True)
    def clean(self):
        self.answer=self.answer.replace(" ","")
        try:
            obj1=json.loads(self.allOptions)
        except:
            raise ValidationError("Can not Decoded by json")
        if type(obj1) is not list:
            raise ValidationError("allOptions field must be a list")
        if self.answer not in obj1:
            raise ValidationError("Answer must be in the options")

class quizAttempt(models.Model):
    student=models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    quiz=models.ForeignKey(Quiz,null=True,on_delete=models.CASCADE)
    startTime=models.DateTimeField(null=True,blank=True)
    choosenOptions=models.TextField(null=True,blank=True)
    marks=models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    def clean(self):
        obj=quizAttempt.objects.filter(student=self.student,quiz=self.quiz).count()
        if obj>=self.quiz.allowedAttempt:
            raise ValidationError("You have used your all attempts") 
        if self.marks<=0:
            raise ValidationError("marks can not be negative!")
        try:
            obj=json.loads(self.choosenOptions)
        except:
            raise ValidationError("Can not Decoded by json")
        
        if type(obj) is not list:
            raise ValidationError("allOptions must be a list of dict")



