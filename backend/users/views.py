import re
from rest_framework.views import exception_handler
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .serializers import UserSerializer
from django.core.mail import send_mail
from django.conf import settings
import string
import secrets
from .models import UserData
from .permissions import IsSuperUser

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is None:
        # If the exception is not handled by DRF, return a custom JSON response
        response = Response(
            {'error': 'Database currently unavailable. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


User = get_user_model()

class Me(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

class Users(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = User.objects.all()
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(username__icontains=search_query) | queryset.filter(email__icontains=search_query)
        return queryset

class CustomUserCreateView(APIView):
    permission_classes = [IsAuthenticated & IsSuperUser]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        is_staff = request.data.get('is_staff', False)
        is_superuser = request.data.get('is_superuser', False)
        sex = request.data.get('sex', '')
        age = request.data.get('age', None)

        if not username or not email:
            return Response(
                {'error': 'Username and email are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not re.match(EMAIL_REGEX, email):
            return Response(
                {'error': 'Invalid email format.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(12))

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=is_staff,
                is_superuser=is_superuser,
            )

            UserData.objects.create(user=user, sex=sex, age=age)

            send_mail(
                subject='Doccano account',
                message=f'Your Doccano account has been created successfully.\nYour username: {username}\nYour password: {password}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return Response(
                {'message': 'User created successfully.'},
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError as e:
            return Response(
                {'error': 'Database error. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )