from django.contrib import admin
from .models import Profile,Course,Progress,Quiz,Question,quizAttempt


admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(Progress)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(quizAttempt)
# Register your models here.
