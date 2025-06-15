import re
from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .serializers import UserSerializer, UserPolymorphicSerializer
from django.core.mail import send_mail
from django.conf import settings
import string
import secrets
from .models import UserData
from .permissions import IsSuperUser

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

User = get_user_model()

class Me(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

class UserList(generics.ListCreateAPIView): 
    queryset = User.objects.all()
    serializer_class = UserPolymorphicSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("username", "email")
    ordering_fields = ["username", "email", "date_joined"]
    ordering = ["-date_joined"]
    
    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated & IsSuperUser]
        return super().get_permissions()

    def get_queryset(self):
        queryset = User.objects.all()

        if not self.request.user.is_staff:
            return queryset.filter(id=self.request.user.id)

        queryset = queryset.filter(userdata__created_by=self.request.user) | User.objects.filter(id=self.request.user.id)
 
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(
                username__icontains=search_query
            ) | queryset.filter(
                email__icontains=search_query
            )
        return queryset
    
class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserPolymorphicSerializer
    lookup_url_kwarg = "user_id"
    
    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated & IsSuperUser]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        # Non-admins can only access their own profile
        if not self.request.user.is_superuser:
            return queryset.filter(id=self.request.user.id)
        # Admins can only access users they created
        return queryset.filter(userdata__created_by=self.request.user) | User.objects.filter(id=self.request.user.id)

class CustomUserCreateView(APIView):
    permission_classes = [IsAuthenticated & IsSuperUser]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
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
                first_name=first_name,
                last_name=last_name,
                password=password,
                is_staff=is_staff,
                is_superuser=is_superuser,
            )

            UserData.objects.create(user=user, sex=sex, age=age, created_by=request.user)

            email_sent = False
            try:
                send_mail(
                    subject='Doccano account',
                    message=f'Your Doccano account has been created successfully.\nYour username: {username}\nYour password: {password}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                email_sent = True
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send email to {email}: {str(e)}")

            if email_sent:
                return Response(
                    {'message': 'User created successfully. Email sent.'},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {
                        'message': 'User created successfully but email could not be sent.',
                        'warning': 'The user account was created, but the notification email failed to send.',
                        'username': username,
                        'password': password
                    },
                    status=status.HTTP_201_CREATED,
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )