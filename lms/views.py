from decimal import Decimal
from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes,authentication_classes,parser_classes
from rest_framework.response import Response
from .serializers import UserSerializer,DashboardSerializer,CourseSerializer,CourseCreateSerializer,QuizSerializer,QuestionsSerializer,ResultSerializer,ProfileSerializer
from rest_framework.parsers import MultiPartParser
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import login,logout,authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Profile, Progress,Course,Quiz,Question,Result
import json


@api_view(['POST'])
def SignUp(request,*args, **kwargs):
    serializer=UserSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'status':403,'errors':serializer.errors})
    serializer.save()
    user=User.objects.get(username=serializer.data['username'])
    profile=Profile.objects.get(user=user)
    if request.data.get('role'):
        profile.role=(request.data.get('role'))

    profile.save()
    token,created=Token.objects.get_or_create(user=user)
    return Response({'status':200,'payload':serializer.data,'token':str(token)})


@api_view(['POST'])
def SignIn(request,*args, **kwargs):
    
    username=request.data.get('username')
    password=request.data.get('password')
    try:
        user=authenticate(request,username=username,password=password)
        login(request,user)
    except:
        return Response({'status':403,'error':'Username or Password Incorrect!'})
    user=User.objects.get(username=username)
    token,created=Token.objects.get_or_create(user=user)
    return Response({'status':200,'username':username,'token':str(token)})



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getProfile(request,*args, **kwargs):
    user=request.user
    profile=Profile.objects.get(user=user)
    serializer=ProfileSerializer(profile,many=False)
    if profile.role=="Instructor":
        #if the user is Instructor we will also be sending details of course created by him
        courseCreated=Course.objects.filter(Instructor=request.user).values()
        return Response({'status':200,'payload':{
            'data':serializer.data,
            'coursesCreated':courseCreated,
        }})
        
    return Response ({'status':200,"payload":{"data":serializer.data}})


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def updateProfile(request,*args, **kwargs):
    user=request.user
    profile=Profile.objects.get(user=user)
    if request.data.get('user'):
        if profile.user.id!=request.gata.get('user'):
            return Response({"status":403,"error":"You can not change user associated with the profile"})
    serializer=ProfileSerializer(instance=profile,data=request.data)
    if not serializer.is_valid():
        return Response({'status':400,'error':serializer.errors})
    serializer.save()

    return Response ({'status':200,"payload":serializer.data})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getEnrolledStudent(request,pk,*args, **kwargs):
    try:
        course=Course.objects.get(id=pk)
    except:
        return Response({'status':404,"error":"Course with this id not found!"})
    if request.user!=course.Instructor:
        return Response({'status':403,'error':"Only Instructor of this course can see this page"})
    #getting all the user that have enrolled that particular course
    #note that coursesEnrolled is an many to many field
    profile=Profile.objects.filter(coursesEnrolled__in=[course,])
    serializer=ProfileSerializer(profile,many=True)
    return Response ({'status':200,'payload':serializer.data})



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])

def home(request,*args, **kwargs):
    
    user=request.user
    progress_obj=Progress.objects.filter(Student=user)
    #dashboardSerializer returns the details of all the course in which he is enrolled in and its progress of Student
    serializer=DashboardSerializer(progress_obj,many=True)
    return Response({'status':200,'payload':serializer.data})


#this view gives us list of all the courses available
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def courseListView(request,*args, **kwargs):
    obj=Course.objects.all()
    serializer=CourseSerializer(obj,many=True)
    return Response({'status':200,'payload':serializer.data})


#view only for Instructor for creating courses
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createCourseView(request,*args, **kwargs):
    profile=Profile.objects.get(user=request.user)
    #checking if user is Instructor or not
    if profile.role!="Instructor":
        return Response({'status':401,'error':"Students can't create course!"})
    serializer=CourseCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({'status':400,'errors':serializer.errors})
    try:
        serializer.save(Instructor=request.user)
    except:
        #it will happen when the unique constraint of the course model will fail
        return Response({'status':400,'error':"Course with same course code already Exits!"})

    return Response({'status':200,'payload':serializer.data})

@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def editCourse(request,pk,*args, **kwargs):
    course=Course.objects.get(id=pk)
    #checking if user is the course instructor
    if course.Instructor != request.user:
        return Response({'status':401,'error':"You are not Authorised to edit this Course"})
    serializer=CourseCreateSerializer(instance=course,data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'status':200,'payload':serializer.data})
    return Response({'status':400,'errors':serializer.errors})




@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def toggleEnrollCourse(request,*args, **kwargs):
    courseCode=request.data.get('code')
    InstructorUsername=request.data.get('Instructor')
    print(InstructorUsername)
    Instructor=User.objects.get(username=InstructorUsername)
    courseObj=Course.objects.get(code=courseCode,Instructor=Instructor)
    progress=Progress.objects.filter(course=courseObj,Student=request.user)
    #if progress of that course for that user is not created which means he is not enrolled
    if not progress:
        progressObj=Progress.objects.create(course=courseObj,Student=request.user)
        progressObj.save()
        profile=Profile.objects.get(user=request.user)
        profile.coursesEnrolled.add(courseObj)
    else:
        #else we are unenrolling the course
        progress.delete()
        profile=Profile.objects.get(user=request.user)
        profile.coursesEnrolled.remove(courseObj)
        return Response({'status':200,'payload':'Course UnEnrolled SuccessFully!'})
    
    serializer=DashboardSerializer(progressObj,many=False)
    return Response({'status':200,'payload':serializer.data})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def courseDetails(request,pk,*args, **kwargs):
    #getting the course
    try:
        course=Course.objects.get(id=pk)
    except:
        return Response({'status':404,'error':"course not found!"})
    quiz=Quiz.objects.filter(course=course)
    quizSerializer=QuizSerializer(quiz,many=True)
    courseSerializer=CourseSerializer(course,many=False)
    #sending the course deatials along with the quiz details associated with that course
    payload={
        'course-details':courseSerializer.data,
        'course-quizes':quizSerializer.data,
    }
    return Response({'status':200,'payload':payload})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createQuiz(request,*args, **kwargs):
    #grabbing course id and getting course object
    pk=request.data.get('CourseId')
    try:
        course=Course.objects.get(id=pk)
    except:
        return Response({'status':404,'error':'Course not found'})
    #checking if user is course Instructor
    if course.Instructor != request.user:
        return Response({'status':401,'error':"You are not Authorised to create Quiz"})
    serializer=QuizSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'status':400,'errors':serializer.errors})
    serializer.save(course=course)
    return Response({'status':200,'payload':serializer.data})

@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def editQuiz(request,pk,*args, **kwargs):
    #trying to get the quiz
    try:
        quiz=Quiz.objects.get(id=pk)
    except:
        return Response({'status':404,'error':"Quiz does not exist!"})
    course=quiz.course
    #checking if user is course instructor
    if course.Instructor != request.user:
        return Response({'status':401,'error':"You are not Authorised to edit this Quiz"})
    serializer=QuizSerializer(instance=quiz,data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'status':200,'payload':serializer.data})
    return Response({'status':400,'errors':serializer.errors})



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def addQuizQuestions(request,*args, **kwargs):
    pk=request.data.get('quizId')
    #trying to get the quiz of id is pk
    try:
        quiz=Quiz.objects.get(id=pk)
    except:
        return Response({'status':404,'error':"Quiz not found!"})
    course=quiz.course
    #checking if user is course instructor
    if course.Instructor != request.user:
        return Response({'status':401,'error':"You are not Authorised to create Questions in this Quiz"})
    
    serializer=QuestionsSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'status':400,'errors':serializer.errors})
    #attaching quiz and allOptions
    serializer.save(quiz=quiz,allOptions=json.dumps(request.data['opt']))

    question=Question.objects.filter(id=serializer.data.get('id')).values()
    print(json.loads(question[0]['allOptions'])[0])
    return Response({'status':200,'payload':serializer.data})


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def editQuestion(request,pk,*args, **kwargs):
    #get the question
    try:
        question=Question.objects.get(id=pk)
    except:
        return Response({'status':404,'error':"Question associated with this id not found!"})
    #can not change the the quiz associated with the question
    if request.data.get("quizId"):
        print(question.quiz.id)
        if question.quiz.id!=request.data.get("quizId"):
            return Response({"status":403,"error":"Quiz Associated with that question can't be changed!"})
    #checking if user is the course instructor
    if request.user!=question.quiz.course.Instructor:
        return Response({'status':"401","error":"You are not Instructor of this course!"})

    serializer=QuizSerializer(instance=question,data=request.data)
    if not serializer.is_valid():
        return Response({'status':"403","error":serializer.errors})
    
    serializer.save()   
    question=Question.objects.get(id=pk)
    #getting allOptions and convering it back to the list
    allOptions=json.loads(question.allOptions)
    
    if request.data.get('changedOption'):
        for option in request.data.get('changedOption'):
            #every option has two things one is the id which is index of the list of allOptions and option 
            #the value of new option
            allOptions[option['id']]=option['option']
            print(allOptions)
            question.allOptions=json.dumps(allOptions)
        question.save()
                    
    serializer1=QuestionsSerializer(question,many=False)
    return Response({"status":200,"payload":serializer1.data})




@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def showQuiz(request,pk,*args, **kwargs):
    #trying to get the quiz
    try:
        quiz=Quiz.objects.get(id=pk)
    except:
        return Response({'status':404,'error':'quiz with that id not Found!'})
    course=quiz.course
    profile=Profile.objects.get(user=request.user)
    #checking if Student enrolled in this course or not
    if course not in profile.coursesEnrolled:
        return Response({'status':401,'error':"Enroll in Course First!"})
    questions=Question.objects.filter(quiz=quiz).values()
    #getting all questions seting answer to empty string as meausure of security and converting all the options 
    #from string to list 
    for question in questions:
        question['allOptions']=json.loads(question['allOptions'])
        question['answer']=""
    serializer=QuizSerializer(quiz,many=False)
    payload={
        'quiz':serializer.data,
        'questions':questions
    }
    return Response({'status':200,'payload':payload})



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def genrateResult(request,*args, **kwargs):
        #getting all the option choosen by the Student
        choosenOptions=request.data.get('choosenOptions')
        try:
            #trying to get the quiz 
            quiz=Quiz.objects.get(id=request.data.get('quizId'))
        except:
            return Response({'status':404,'error':'quiz with that id not Found!'})
        marks=Decimal(0)
        course=quiz.course
        profile=Profile.objects.get(user=request.user)
        #checking if he has enrolled the course or not
        if course not in profile.coursesEnrolled:
            return Response({'status':401,'error':"Enroll in Course First!"})
        
        #calculating the result
        for solution in choosenOptions:
            try:
                question=Question.objects.filter(id=solution['questionId']).values()
                print(question[0]['answer'])
                answer=question[0]['answer']
                if answer == solution['answer']:
                    marks+=question[0]['maxMarks']
            except:
                return Response({'status':404,'error':'Question with that id not Found!'})
            
        try:
            result=Result.objects.create(student=request.user,quiz=quiz,marks=marks,choosenOptions=json.dumps(choosenOptions))
            result.save()

            return Response({'status':200,'payload':{
                "marks":marks,
                "quizId":request.data.get('quizId')
            }})
        except:
            return Response({'status':403,'error':"Cant Not Attempt the Quiz Twice"})





@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def showResult(request,pk,*args, **kwargs):

    #checking if the quiz exists
    try:
        quiz=Quiz.objects.get(id=pk)
    except:
        return Response({'status':403,'error':"Quiz does not exist!"})
    result=Result.objects.filter(quiz=quiz,user=request.user).values()
    #here we are checking if there is a result for that user for that particular quiz
    if len(result)==0:
        return Response({'status':401,'error':"Take the Quiz First to see results!"})
    #here we are changing the choosenOptions from string to list of objects
    for solution in result[0]['choosenOptions']:
        solution=json.loads(solution)
    
    return Response({'status':200,'payload':result})


# View to delete a Quiz require pk to be send in url
#and user must be the course instructor

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteQuiz(request,pk,*args, **kwargs):
    try:
        quiz=Quiz.objects.get(id=pk)
    except:
        return Response({'status':404,"error":"Quiz not Found!"})
    if request.user!=quiz.course.Instructor:
        return Response({'status':"401","error":"You are not Instructor of this course!"})
    quiz.delete()
    return Response({'status':200,"palyload":"quiz deleted !"})



# View to delete a Question require pk to be send in url
#user must be the course Instructor

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteQuestion(request,pk,*args, **kwargs):
    try:
        question=Question.objects.get(id=pk)
    except:
        return Response({'status':404,"error":"Question not Found!"})
    if request.user!=question.quiz.course.Instructor:
        return Response({'status':"401","error":"You are not Instructor of this course!"})
    question.delete()
    return Response({'status':200,"palyload":"Question deleted !"})

