from django.urls import path
from UserApp.api.views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = 'User'

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-change/', PasswordChangeView.as_view(), name='password-change'),
    path('risk/', RiskView.as_view(), name='risk'),
    path('investment/', InvestmentView.as_view(), name='investment'),
    path('email-change/', EmailChangeView.as_view(), name='email-change'),
    path('user-change/', UserChangeView.as_view(), name='user-change'),
    path('forget-password/', ForgetPasswordView.as_view(), name='forget-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('image/', ImageView.as_view(), name='image'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)