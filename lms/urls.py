from django.urls import path
from .views import home,SignIn,SignUp,courseListView,createCourseView,toggleEnrollCourse,courseDetails,createQuiz,addQuizQuestions,genrateResult,showQuiz,showResult,editCourse,editQuiz,editQuestion,deleteQuestion,deleteQuiz,getProfile,updateProfile,getEnrolledStudent

urlpatterns=[
    path('',home),
    path('signup/',SignUp),
    path('signin/',SignIn),
    path('all-courses/',courseListView),
    path('create-course/',createCourseView),
    path('toggle-enroll-course/',toggleEnrollCourse),
    path('course-details/<int:pk>/',courseDetails),
    path('create-quiz/',createQuiz),
    path('add-questions/',addQuizQuestions),
    path('submit-quiz/',genrateResult),
    path('show-quiz/<int:pk>/',showQuiz),
    path('show-result/<int:pk>/',showResult),
    path('edit-course/<int:pk>/',editCourse),
    path('edit-quiz/<int:pk>/',editQuiz),
    path('edit-questions/<int:pk>/',editQuestion),
    path('delete-quiz/<int:pk>/',deleteQuiz),
    path('delete-question/<int:pk>/',deleteQuestion),
    path('profile/',getProfile),
    path('update-profile/',updateProfile),
    path('get-enrolled-student/<int:pk>/',getEnrolledStudent),

]
