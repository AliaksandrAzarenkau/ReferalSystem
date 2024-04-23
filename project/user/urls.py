from django.urls import path

from user import views

urlpatterns = [
    path('user_login', views.LoginAPIView.as_view(), name='user_login'),
    path('user_auth', views.AuthenticationAPIView.as_view(), name='user_auth'),
    path('user_profile', views.UserProfileAPIView.as_view(), name='user_profile'),
    path('signup', views.get_signup_page, name='signup'),
    path('auth', views.authentication, name='auth'),
    path('profile', views.user_profile, name='profile'),
]
