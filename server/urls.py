
from django.contrib import admin
from django.urls import path,include
from rest_framework.authtoken import views
from lms import urls as lms_urls
from django.conf import settings
from django.conf.urls.static import static  
urlpatterns = [
    path('',include(lms_urls)),
    path('admin/', admin.site.urls),
    path('api-token-auth/', views.obtain_auth_token),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

