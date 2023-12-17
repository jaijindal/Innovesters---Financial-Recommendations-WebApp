from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from django.http import FileResponse
from .serializers import UserSerializer, ImageSerializer
from UserApp.models import UserProfile
from MainApp import settings
from datetime import timedelta

class RegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response({"data": {"error": serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
        

class LogoutView(APIView):
    def post(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Delete the token
            request.user.auth_token.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            # Return an error response
            return Response({"error": "User is not authenticated"}, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')

            if not check_password(current_password, request.user.password):
                return Response({"error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

            if new_password != confirm_password:
                return Response({"error": "New password and confirm password do not match"}, status=status.HTTP_400_BAD_REQUEST)

            request.user.set_password(new_password)
            request.user.save()

            return Response({"success": "Password changed successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_400_BAD_REQUEST)
        

class RiskView(APIView):
    AUTH_ERROR = {"error": "User is not authenticated"}
    RISK_NOT_PROVIDED_ERROR = {"error": "Risk level not provided"}

    def get(self, request):
        if request.user.is_authenticated:
            risk = request.user.userprofile.risk
            risk_choices = dict(UserProfile.RISK_CHOICES)
            return Response({"risk": risk, "risk_choices": risk_choices}, status=status.HTTP_200_OK)
        else:
            return Response(self.AUTH_ERROR, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        if request.user.is_authenticated:
            new_risk = request.data.get('risk')
            if new_risk is not None:
                request.user.userprofile.risk = new_risk
                request.user.userprofile.save()
                return Response({"success": "Risk level updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(self.RISK_NOT_PROVIDED_ERROR, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(self.AUTH_ERROR, status=status.HTTP_400_BAD_REQUEST)
        
class InvestmentView(APIView):
    INVESTMENT_NOT_PROVIDED_ERROR = {"error": "Investment goal not provided"}

    def get(self, request):
        if request.user.is_authenticated:
            investment = request.user.userprofile.investment
            investment_choices = dict(UserProfile.INVESTMENT_CHOICES)
            return Response({"investment": investment, "investment_choices": investment_choices}, status=status.HTTP_200_OK)
        else:
            return Response(RiskView.AUTH_ERROR, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        if request.user.is_authenticated:
            new_investment = request.data.get('investment')
            if new_investment is not None:
                request.user.userprofile.investment = new_investment
                request.user.userprofile.save()
                return Response({"success": "Investment goal updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(self.INVESTMENT_NOT_PROVIDED_ERROR, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(RiskView.AUTH_ERROR, status=status.HTTP_400_BAD_REQUEST)


class EmailChangeView(APIView):
    EMAIL_NOT_PROVIDED_ERROR = {"error": "Email not provided"}

    def get(self, request):
        if request.user.is_authenticated:
            email = request.user.email
            return Response({"email": email}, status=status.HTTP_200_OK)
        else:
            return Response(RiskView.AUTH_ERROR, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        if request.user.is_authenticated:
            new_email = request.data.get('email')
            if new_email is not None:
                if User.objects.filter(email=new_email).exists():
                    return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
                request.user.email = new_email
                request.user.save()
                return Response({"success": "Email updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(self.EMAIL_NOT_PROVIDED_ERROR, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(RiskView.AUTH_ERROR, status=status.HTTP_400_BAD_REQUEST)


class UserChangeView(APIView):
    USERNAME_NOT_PROVIDED_ERROR = {"error": "Username not provided"}

    def get(self, request):
        if request.user.is_authenticated:
            username = request.user.username
            return Response({"username": username}, status=status.HTTP_200_OK)
        else:
            return Response(RiskView.AUTH_ERROR, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        if request.user.is_authenticated:
            new_username = request.data.get('username')
            if new_username is not None:
                if User.objects.filter(username=new_username).exists():
                    return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
                request.user.username = new_username
                request.user.save()
                return Response({"success": "Username updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(self.USERNAME_NOT_PROVIDED_ERROR, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(RiskView.AUTH_ERROR, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response('Email not provided', status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response('User not found', status=status.HTTP_404_NOT_FOUND)

        if user.userprofile.last_password_reset_request and user.userprofile.last_password_reset_request > timezone.now() - timedelta(minutes=1):
            return Response('You can only request a password reset once every 1 minute', status=status.HTTP_429_TOO_MANY_REQUESTS)

        user.userprofile.last_password_reset_request = timezone.now()
        user.userprofile.save()

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = "http://172.21.148.171:3000/reset-password/"
        mail_subject = 'Reset your password.'
        
        message = f"""
        Hi {user.username},

        You have requested a password reset. Please click on the link below to reset your password:

        {current_site}?uid={uid}&token={token}

        If you did not request this password reset, please ignore this email.

        Thanks,
        TechTitans
        """

        send_mail(
            mail_subject,
            message,
            'TechTitans@gmail.com',
            [user.email],
            fail_silently=False,
        )
        return Response('Password reset email sent', status=status.HTTP_200_OK)
    

class ResetPasswordView(APIView):
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not uid or not token or not new_password:
            return Response('Missing parameters', status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response('Invalid uid', status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response('Invalid token', status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response('Password reset successful')
    

class ImageView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.image:
                file_serializer = ImageSerializer(user_profile)
                return Response(file_serializer.data, status=status.HTTP_200_OK)
            else:
                default_image_path = settings.MEDIA_ROOT / 'profile_images/default.jpg'
                return FileResponse(open(default_image_path, 'rb'), content_type='image/jpeg')
        else:
            return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        
    def post(self, request):
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user=request.user)
            old_image = user_profile.image
            file_serializer = ImageSerializer(user_profile, data=request.data)
    
            if file_serializer.is_valid():
                if old_image and old_image != 'default.jpg':
                    old_image.delete(save=False)
                file_serializer.save()
                return Response(file_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

