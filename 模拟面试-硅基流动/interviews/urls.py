from django.urls import path
from . import views

urlpatterns = [
    path('api/chat', views.chat, name='chat'),
    path('api/job-suggestions', views.job_suggestions, name='job_suggestions'),
    path('api/report', views.get_report, name='get_report'),
    path('api/register', views.register_view, name='register'),
    path('api/login', views.login_view, name='login'),
    path('api/logout', views.logout_view, name='logout'),
    path('api/user', views.get_user_info, name='user_info'),
    path('api/history', views.history_view, name='history'),
    path('api/delete-interview', views.delete_interview, name='delete_interview'),
    path('api/change-password', views.change_password, name='change_password'),
]
