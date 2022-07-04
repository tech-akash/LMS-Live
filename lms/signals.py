from django.db.models import signals
from decimal import Decimal
# from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core import serializers
from .models import Profile,Question,Quiz,Result,Progress
import json
@receiver(signals.post_save,sender=User)
def create_profile(sender,instance,*args, **kwargs):
    if kwargs['created']:
        profile=Profile.objects.create(user=instance)
        profile.save()

@receiver(signals.post_save,sender=Question)
def add_marks(sender,instance,*args, **kwargs):
    if kwargs['created']:
        data = serializers.serialize('json', [instance,])
        json_data = json.loads(data)
        quizId=json_data[0]['fields']['quiz']
        marks=json_data[0]['fields']['maxMarks']
        quiz=Quiz.objects.get(id=quizId)
        quiz.totalMarks+=Decimal(marks)
        quiz.save()
        course=quiz.course
        course.totalMarks+=Decimal(marks)
        course.save()

        # profile=Quiz.objects.get()
        # profile.save()

@receiver(signals.post_save,sender=Result)
def update_progress(sender,instance,*args, **kwargs):
    if kwargs['created']:
        data = serializers.serialize('json', [instance,])
        json_data = json.loads(data)
        quizId=json_data[0]['fields']['quiz']
        studentId=json_data[0]['fields']['student']
        marks=json_data[0]['fields']['marks']
        Student=User.objects.get(id=studentId)
        quiz=Quiz.objects.get(id=quizId)
        course=quiz.course
        progress=Progress.objects.get(course=course,Student=Student)
        progress.currMarks+=Decimal(marks)
        progress.save()


